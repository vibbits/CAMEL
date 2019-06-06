from flask_restful import request, reqparse
from MySQLdb.cursors import DictCursor
from Camel import CamelResource
from Camel.field import FieldList
from Camel.auth import is_authenticated

import io
import csv

def _compose_query(where_base = [], where_field = [], where_ref = []):
    '''
    Compose the SQL query to fetch a filtered list of experiments

    :param where_base: list of WHERE statements for main query
    :param where_field: list of WHERE statements for experiment_fields sub_query
    :param where_ref: list of WHERE statements for references_fields sub_query
    '''
    base = ("SELECT e.`id` AS `experiment_id`, e.`name`, "
            "f.`id` AS `field_id`, f.`title` AS `field_title`, f.`weight`, "
            "ef.`id` as value_id, "
            "ef.`value_INT`, ef.`value_VARCHAR`, ef.`value_DOUBLE`, ef.`value_BOOL`, ef.`value_TEXT` "
            "FROM `experiments` e "
            "LEFT JOIN `experiments_fields` ef ON e.`id` = ef.`experiment_id` "
            "LEFT JOIN `fields` f ON ef.`field_id` = f.`id` ")

    field_filter = ("e.`id` IN (SELECT ef_filter.`experiment_id` "
                         "FROM `experiments_fields` ef_filter "
                         "WHERE {} ) ")

    ref_filter = ("e.`id` IN (SELECT er_filter.`experiment_id` "
                  "FROM `experiments_references` er_filter "
                  "JOIN `references` r_filter ON er_filter.`reference_id` = r_filter.`id` "
                  "WHERE {} ) ")

    
    order = " ORDER BY e.`id`, f.`weight`"

    where = []
    where+= where_base
    for wf in where_field:
        wf_sql = field_filter.format(wf)
        where.append(wf_sql)
        
    for wr in where_ref:
        wr_sql = ref_filter.format(wr)
        where.append(wr_sql)

    sql = base
    if len(where) > 0:
        sql+=" WHERE "+' AND '.join(where)
        
    sql+= order

    return sql

def _compact(res, field_types, db):
    '''
    Gather all result values from the query and group them by experiment.

    :return a list of dictionaries, one per experiment 
    '''
    ##Combine all field/value results into a 'summary' (one entry per experiment)
    summary = {}
    for entry in res:
        experiment_id = entry['experiment_id']
        if experiment_id not in summary:
            summary[experiment_id] = {}
            summary[experiment_id]['name'] = entry['name']
            summary[experiment_id]['fields'] = {}
        
        field_id = entry['field_id']
        if field_id is None:
            continue
        
        field_type = field_types[field_id]
        field_value = entry['value_'+field_type]
            
        if field_id not in summary[experiment_id]['fields']:
            summary[experiment_id]['fields'][field_id] = {}

        value_id = entry['value_id']
        summary[experiment_id]['fields'][field_id][value_id] = field_value

    ##generate a list from gathered summary results and add the references to each entry
    result = []
    for exp_id in summary:
        exp = summary[exp_id]
        
        ##ID
        exp['id'] = exp_id

        ##References
        sql = ("SELECT r.`id`, r.`authors`, r.`title`, r.`journal`, r.`year`, r.`pages`, r.`pubmed_id`, r.`url` "
               "FROM `references` r "
               "JOIN `experiments_references` er ON r.`id` = er.`reference_id` "
               "WHERE er.`experiment_id` = %(ID)s")

        c = db.cursor(DictCursor)
        c.execute(sql, {'ID': exp_id})
        res = c.fetchall()
        c.close()            
        exp['references'] = res

        result.append(exp)

    return result

def _map_field_types():
    '''
    :return a mapping of field id's to field type (VARCHAR, TEXT, INT, BOOL)
    '''
    fieldList = FieldList()
    rows = fieldList.retrieveFieldData()
            
    field_types = {}
    for row in rows:
        field_types[row['id']] = row['type_column'].split('_')[1]

    return field_types


            
class ExperimentList(CamelResource):
    def _add_field_filters(self, field_id, field_type, value):
        if field_type == 'VARCHAR' or field_type == 'TEXT':
            filter_query = ("(ef_filter.`field_id` = %(FieldID_{field_id})s AND ef_filter.`value_{field_type}` "
                            "LIKE CONCAT('%%', %(FieldValue_{field_id})s ,'%%')) ").format(field_id=field_id, field_type=field_type)

            self.tokens["FieldID_{}".format(field_id)] = field_id
            self.tokens["FieldValue_{}".format(field_id)] = value
            self.where_field.append(filter_query)

        elif field_type == 'INT' or field_type == 'DOUBLE':
            filter_query = "(ef_filter.`field_id` = %(FieldID_{field_id})s ".format(field_id=field_id)
            self.tokens["FieldID_{}".format(field_id)] = field_id

            if 'min_'+str(field_id) in request.args:
                min_value = request.args['min_'+str(field_id)]
                filter_query+= "AND ef_filter.`value_{field_type}` >= %(FieldMinValue_{field_id})s ".format(field_type=field_type, field_id=field_id)
                self.tokens["FieldMinValue_{}".format(field_id)] = min_value
            if 'max_'+str(field_id) in request.args:
                max_value = request.args['max_'+str(field_id)]
                filter_query+= "AND ef_filter.`value_{field_type}` <= %(FieldMaxValue_{field_id})s ".format(field_type=field_type, field_id=field_id)
                self.tokens["FieldMaxValue_{}".format(field_id)] = max_value

            filter_query+= ") "
            self.where_field.append(filter_query)

        elif field_type == 'BOOL':
            bool_value = 1 if value=='true' else 0
            filter_query = ("(ef_filter.`field_id` = %(FieldID_{field_id})s "
                            "AND ef_filter.`value_BOOL` = %(FieldValue_{field_id})s) ").format(field_id=field_id)
            self.tokens["FieldID_{}".format(field_id)] = field_id
            self.tokens["FieldValue_{}".format(field_id)] = bool_value
            self.where_field.append(filter_query)
        
    def _add_ref_filters(self, field_id, value):
        ref_parts = field_id.split('_', 1)
        if len(ref_parts) == 1 or (ref_parts[0] != 'min' and ref_parts[0] != 'max'):
            ref_filter_query = "(r_filter.`{ref_field}` LIKE CONCAT('%%', %(RefValue_{ref_field})s, '%%')) ".format(ref_field=field_id)
            self.tokens['RefValue_{}'.format(field_id)] = value
            self.where_ref.append(ref_filter_query)
        else:
            if field_id == 'min_year':
                ref_filter_query = "r_filter.`year` >= %(MinYear)s "
                self.tokens['MinYear'] = value
            elif field_id == 'max_year':
                ref_filter_query = "r_filter.`year` <= %(MaxYear)s "
                self.tokens['MaxYear'] = value
            self.where_ref.append(ref_filter_query)

    def retrieveExperimentData(self):
        '''
        Gather all experiment data, filtered by field and reference

        Filters are key_value pairs with the key formatted like:
        - ExperimentName
        - <int> (int being a field id)
        - min_<int> | max_<int> (min/max values for an integer field, <int> being a field id)
        - ref_<field> (reference data, field being 'authors', 'journal' or 'title'
        - ref_min_year | ref_max_year (reference year min/max values)
        '''
        self.tokens = {}                        
                        
        ##Name filter
        self.where_base = []

        ##Field filters
        self.where_field = []
        self.where_ref = []
        field_types = _map_field_types()
        
        for key in request.args:
            value = request.args[key]

            if key == 'ExperimentName':
                self.where_base.append("e.`name` LIKE CONCAT('%%', %(ExperimentName)s ,'%%') ")
                self.tokens['ExperimentName'] = request.args['ExperimentName']
                continue

            key_parts = key.split('_', 1)
            if len(key_parts) == 2:
                field_prefix = key_parts[0]
                field_id = key_parts[1]                
            else:
                field_prefix = ''
                field_id = key

            ## Field filter
            if field_id.isnumeric():
                field_id = int(field_id)
                field_type = field_types[field_id]
                self._add_field_filters(field_id, field_type, value)

            ## Ref filter
            elif field_prefix == 'ref':
                self._add_ref_filters(field_id, value)

                
        c = self.db.cursor(DictCursor)
        sql = _compose_query(self.where_base, self.where_field, self.where_ref)

        c.execute(sql, self.tokens)
        res = c.fetchall()
        c.close()

        result = _compact(res, field_types, self.db)
        return result

    def csv(self):
        '''
        Retrieve all (filtered) experiment data and format as a CSV string
        '''
        output = io.StringIO()
        writer = csv.writer(output,
                            dialect="excel",
                            quoting=csv.QUOTE_MINIMAL)
        data = self.retrieveExperimentData()

        fieldList = FieldList()
        fields = fieldList.retrieveFieldData()
        
        ## Write header
        header_fields = []
        header_fields.append("id")
        header_fields.append("name")
        header_fields.append("paper_title")
        header_fields.append("paper_authors")
        header_fields.append("paper_journal")
        header_fields.append("paper_year")
        header_fields.append("paper_pages")
        header_fields.append("paper_url")
        header_fields.append("pubmed_id")

        for f in fields:
            header_fields.append(f['title'])
            
        writer.writerow(header_fields)

        ## Write data
        for exp in data:
            row = []
            row.append(exp['id'])
            row.append(exp['name'])
            
            titles=[]
            authors=[]
            journals=[]
            years=[]
            pages=[]
            urls=[]
            pubmed_ids=[]
            for ref in exp['references']:
                titles.append(ref['title'])
                authors.append(ref['authors'])
                journals.append(ref['journal'])
                years.append(ref['year'])
                pages.append(ref['pages'])
                urls.append(ref['url'])
                pubmed_ids.append(ref['pubmed_id'])

            row.append('\n'.join([t if t is not None else '' for t in titles]))
            row.append('\n'.join([a if a is not None else ''for a in authors]))
            row.append('\n'.join([j if j is not None else '' for j in journals]))
            row.append('\n'.join([str(y) for y in years]))
            row.append('\n'.join([p if p is not None else '' for p in pages]))
            row.append('\n'.join([u if u is not None else '' for u in urls]))
            row.append('\n'.join([p if p is not None else '' for p in pubmed_ids]))

            for field in fields:
                field_id = field['id']
                if field_id in exp['fields']:
                    field_values = exp['fields'][field_id]                
                    row.append('\n'.join([str(f) if f is not None else '' for f in field_values]))
                else:
                    row.append('')                    
            
            writer.writerow(row)
            
        return output.getvalue()
            
    
    def get(self):
        result = self.retrieveExperimentData()
        return result

    def post(self):
        pass


class Experiment(CamelResource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()

        ##PUT arguments
        self.reqparse.add_argument('name', type = str, location = 'json')
        self.reqparse.add_argument('fields', type = dict, location = 'json')
        self.reqparse.add_argument('references', type = list, location = 'json')

        super(Experiment, self).__init__()
    
    def get(self, id):
        where_base = ["e.`id` = %(id)s"]
        tokens = {'id': id}
        
        c = self.db.cursor(DictCursor)
        sql = _compose_query(where_base)
        c.execute(sql, tokens)
        res = c.fetchall()
        c.close()
        field_types = _map_field_types()
        result = _compact(res, field_types, self.db)
        
        return result[0]
    

    def put(self, id):        
        ## Without authentication, the user can only make
        ## suggestions, but never overwrite an entry.
        suggestion = not is_authenticated()

        args = self.reqparse.parse_args()

        cursor = self.db.cursor()
        if args['name']:
            name = args['name']
            sql = "UPDATE `experiments` SET `name` = %(name)s WHERE `id` = %(id)s"
            cursor.execute(sql, {'id': id, 'name': name})
                           
        if args['fields']:
            field_types = _map_field_types()
            
            fields = args['fields']
            for field_id, values in fields.items():
                field_type = field_types[int(field_id)]
                for value_id, value in values.items():
                    id_parts = value_id.split('_') 
                    if len(id_parts) == 2 and id_parts[0] == 'new':
                        ##Insert new value
                        sql = ("INSERT INTO `experiments_fields` "
                               "(`experiment_id`, `field_id`, `value_{type_col}`) "
                               "VALUES (%(exp_id)s, %(field_id)s, %(val)s) ").format(type_col = field_type)
                        cursor.execute(sql, {'exp_id': id, 'field_id': field_id, 'val': value})
                    else:
                        if value is not None:
                            ##Update existing value
                            sql = "UPDATE `experiments_fields` SET `value_{type_col}` = %(value)s WHERE `id`=%(val_id)s".format(type_col=field_type)
                            cursor.execute(sql, {'val_id': value_id, 'value': value})
                        else:
                            ##Delete value
                            sql = "DELETE FROM `experiments_fields` WHERE `id` = %(val_id)s"
                            cursor.execute(sql, {'val_id': value_id})

        if args['references']:
            for ref in args['references']:                    
                if 'action' not in ref:
                    ##Update existing reference
                    sql = ("UPDATE `references` SET "
                           "`title`=%(title)s, `authors`=%(authors)s, "
                           "`journal`=%(journal)s, `year` = %(year)s, `pages` = %(pages)s, "
                           "`pubmed_id`=%(pubmed_id)s, `url`=%(url)s "
                           "WHERE `id` = %(id)s")
                    cursor.execute(sql, ref)
                else:
                    action = ref['action']                    
                    if action == 'link':
                        ##Link an existing reference to this experiment
                        sql = "INSERT INTO `experiments_references` (`experiment_id`, `reference_id`) VALUES (%(exp_id)s, %(ref_id)s)"
                        cursor.execute(sql, {'exp_id': id, 'ref_id': ref['id']})
                    elif action == 'new':
                        ##Add new reference
                        sql = ("INSERT INTO `references` "
                               "(`title`, `authors`, `journal`, `year`, `pages`, `pubmed_id`, `url`) "
                               "VALUES (%(title)s, %(authors)s, %(journal)s, %(year)s, %(pages)s, %(pubmed_id)s, %(url)s) ")
                        cursor.execute(sql, ref)
                        ref_id = cursor.lastrowid
                        sql = "INSERT INTO `experiments_references` (`experiment_id`, `reference_id`) VALUES (%(exp_id)s, %(ref_id)s)"
                        cursor.execute(sql, {'exp_id': id, 'ref_id': ref_id})
                    elif action == 'unlink':
                        ##Delete the link between reference and experiment without remove the reference
                        ##If no more links exists, the reference will be deleted
                        ##TODO: check if cascading allows this!
                        sql = "DELETE FROM `experiments_references` WHERE `experiment_id` = %(exp_id)s and `reference_id` = %(ref_id)s"
                        cursor.execute(sql, {'exp_id': id, 'ref_id': ref['id']})
                        ##TODO: remove orphan reference
                        
                    
        
        self.db.commit()
        cursor.close()
        
        return "UPDATED", 204
