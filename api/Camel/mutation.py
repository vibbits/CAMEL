from flask_restful import request, reqparse
from MySQLdb.cursors import DictCursor
from pathlib import Path

from Camel import CamelResource
from Camel.field import FieldList
from Camel.auth import login_required
from Camel import config


import io
import shutil
import csv

def _compose_query(where_base = [], where_field = [], not_field = [], where_ref = []):
    '''
    Compose the SQL query to fetch a filtered list of experiments

    :param where_base: list of WHERE statements for main query
    :param where_field: list of WHERE statements for mutations_fields sub_query
    :param where_ref: list of WHERE statements for references_fields sub_query
    '''
    base = ("SELECT e.`id` AS `experiment_id`, mf.`mutation_id`, e.`name`, "
            "f.`id` AS `field_id`, f.`title` AS `field_title`, f.`weight`, "
            "mf.`id` as value_id, "
            "mf.`value_INT`, mf.`value_VARCHAR`, mf.`value_DOUBLE`, mf.`value_BOOL`, mf.`value_TEXT`, mf.`value_ATTACH` "
            "FROM `experiments` e "
            "LEFT JOIN `mutations_fields` mf ON e.`id` = mf.`experiment_id` "
            "LEFT JOIN `fields` f ON mf.`field_id` = f.`id`  ")

    field_filter = ("e.`id` IN (SELECT ef_filter.`mutation_id` "
                         "FROM `mutations_fields` ef_filter "
                         "WHERE {} ) ")
    
    not_field_filter = ("e.`id` NOT IN (SELECT ef_filter.`mutation_id` "
                         "FROM `mutations_fields` ef_filter "
                         "WHERE {} ) ")

    ref_filter = ("e.`id` IN (SELECT er_filter.`mutation_id` "
                  "FROM `experiments_references` er_filter "
                  "JOIN `references` r_filter ON er_filter.`reference_id` = r_filter.`id` "
                  "WHERE {} ) ")

    
    order = " ORDER BY e.`id`, mf.`mutation_id`, f.`weight`"

    where = []
    where+= where_base
    for wf in where_field:
        wf_sql = field_filter.format(wf)
        where.append(wf_sql)

    for nf in not_field:
        nf_sql = not_field_filter.format(nf)
        where.append(nf_sql)
        
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
    Gather all result values from the query and group them by experiment and by mutation.

    :return a dictionary of list of dictionaries, one per mutation 
    '''
    ##Combine all field/value results into a 'summary' (one entry per experiment)
    summary = {}
    for entry in res:
        mutation_id = entry['mutation_id']
        if mutation_id not in summary:
            summary[mutation_id] = {}
            summary[mutation_id]['name'] = entry['name']
            summary[mutation_id]['fields'] = {}
        
        field_id = entry['field_id']
        if field_id is None:
            continue
        
        field_type = field_types[field_id]
        field_value = entry['value_'+field_type]
            
        if field_id not in summary[mutation_id]['fields']:
            summary[mutation_id]['fields'][field_id] = {}

        value_id = entry['value_id']
        summary[mutation_id]['fields'][field_id][value_id] = field_value

    ##generate a list from gathered summary results and add the references to each entry
    result = []
    for mut_id in summary:
        mut = summary[mut_id]
        
        ##ID
        mut['id'] = mut_id

        ##References
        sql = ("SELECT r.`id`, r.`authors`, r.`title`, r.`journal`, r.`year`, r.`pages`, r.`pubmed_id`, r.`url` "
               "FROM `references` r "
               "JOIN `experiments_references` er ON r.`id` = er.`reference_id` "
               "WHERE er.`experiment_id` = %(ID)s")

        c = db.cursor(DictCursor)
        c.execute(sql, {'ID': mut_id})
        res = c.fetchall()
        c.close()            
        # mut['references'] = res

        result.append(mut)

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


def _put_file(uuid, exp_id, field_id, filename):
    '''
    Move tmp file with uuid to its download location with 
    original filename.

    :return: final filename, including possible postfix
    '''
    upload_conf = config['uploads']
    tmp_path = Path(upload_conf['TMP'])
    tmp_file = tmp_path.joinpath(uuid)
        
    target_path = Path(upload_conf['PATH'])
    target_full_path = target_path.joinpath(str(exp_id), str(field_id))
    target_full_path.mkdir(parents=True, exist_ok=True)
    target_file = target_full_path.joinpath(filename)

    postfix = 0
    stem = target_file.stem.split('.')[0]
    while target_file.exists():
        postfix +=1
        postfixed = stem + '_'  + str(postfix)
        new_name = postfixed + ''.join(target_file.suffixes)
        target_file = target_file.parent.joinpath(new_name)
        
    shutil.move(str(tmp_file), str(target_file), copy_function=shutil.copy)

    return target_file.name

def _del_file(exp_id, field_id, filename):
    '''
    Remove file
    '''
    upload_conf = config['uploads']
    target_path = Path(upload_conf['PATH'])
    target_file = target_path.joinpath(str(exp_id), str(field_id), filename)
    try:
        target_file.unlink()
    except FileNotFoundError:
        ## if the file is gone already: mission accimplished
        pass

def _edit_fields(exp_id, fields, field_types, db):
    '''
    Loop over the submitted field dictionary (field id => field data) 
    and insert/update/delete as needed.
    '''
    cursor = db.cursor()
    for field_id, values in fields.items():
        field_type = field_types[int(field_id)]
        for value_id, value in values.items():
            id_parts = value_id.split('_') 
            if len(id_parts) == 2 and id_parts[0] == 'new':                
                ##Insert new value
                ##uploaded attachments need to store the tmp uuid
                if field_type == 'ATTACH':
                    uuid = value['uuid']
                    value = value['filename']
                    value = _put_file(uuid, exp_id, field_id, value)
                
                sql = ("INSERT INTO `mutations_fields` "
                       "(`experiment_id`, `field_id`, `value_{type_col}`) "
                       "VALUES (%(exp_id)s, %(field_id)s, %(val)s) ").format(type_col = field_type)
                cursor.execute(sql, {'exp_id': exp_id, 'field_id': field_id, 'val': value})

            else:
                if type(value) is not dict:
                    ##Update existing value
                    sql = "UPDATE `mutations_fields` SET `value_{type_col}` = %(value)s WHERE `id`=%(val_id)s".format(type_col=field_type)
                    cursor.execute(sql, {'val_id': value_id, 'value': value})
                elif 'action' in value and value['action'] == 'delete':
                    ##Delete value
                    if field_type == 'ATTACH':
                        sql = "SELECT `value_ATTACH` as filename FROM `mutations_fields` WHERE `id` = %(val_id)s"
                        cursor.execute(sql, {'val_id': value_id})
                        row = cursor.fetchone()
                        _del_file(exp_id, field_id, row[0])
                    sql = "DELETE FROM `mutations_fields` WHERE `id` = %(val_id)s"
                    cursor.execute(sql, {'val_id': value_id})
    cursor.close()

def _edit_references(exp_id, refs, db):
    '''
    Loop over the list of submitted references and insert/update/delete as needed. 
    '''
    cursor = db.cursor()

    sql = "SELECT `reference_id` FROM `experiments_references` WHERE `experiment_id` = %(exp_id)s"
    cursor.execute(sql, {'exp_id': exp_id})
    ref_links = cursor.fetchall()
    ref_links = [r[0] for r in ref_links]
    
    for ref in refs:
        if 'action' in ref:
            if ref['action'] == 'new':
                ##Add new reference
                sql = ("INSERT INTO `references` "
                       "(`title`, `authors`, `journal`, `year`, `pages`, `pubmed_id`, `url`) "
                       "VALUES (%(title)s, %(authors)s, %(journal)s, %(year)s, %(pages)s, %(pubmed_id)s, %(url)s) ")
                cursor.execute(sql, ref)
                ref['id'] = cursor.lastrowid
            if ref['action'] == 'delete':
                sql = "DELETE FROM `experiments_references` WHERE `experiment_id` = %(exp_id)s AND `reference_id` = %(ref_id)s"
                cursor.execute(sql, {'exp_id': exp_id, 'ref_id': ref['id']})
                
                ##check if the reference points at other experiments. If not, delete it completely
                sql = "SELECT * FROM `experiments_references` WHERE `reference_id` = %(ref_id)s"
                count = cursor.execute(sql, {'ref_id': ref['id']})
                if count == 0:
                    sql = "DELETE FROM `references` WHERE `id` = %(ref_id)s"
                    cursor.execute(sql, {'ref_id': ref['id']})
            
        if 'action' not in ref or ref['action'] == 'update':
            ##Update existing reference
            sql = ("UPDATE `references` SET "
                   "`title`=%(title)s, `authors`=%(authors)s, "
                   "`journal`=%(journal)s, `year` = %(year)s, `pages` = %(pages)s, "
                   "`pubmed_id`=%(pubmed_id)s, `url`=%(url)s "
                   "WHERE `id` = %(id)s")
            cursor.execute(sql, ref)

        ##insert a link between experiment and reference if it's not there yet.
        if ref['id'] not in ref_links:
            sql = "INSERT INTO `experiments_references` (`experiment_id`, `reference_id`) VALUES (%(exp_id)s, %(ref_id)s)"
            cursor.execute(sql, {'exp_id': exp_id, 'ref_id': ref['id']})
            
    
    cursor.close()

            
class MutationList(CamelResource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()

        ##POST arguments
        self.reqparse.add_argument('name', required = True, type = str, location = 'json')
        self.reqparse.add_argument('fields', type = dict, location = 'json')
        self.reqparse.add_argument('references', type = list, location = 'json')

        super(MutationList, self).__init__()
    
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

        elif field_type == 'ATTACH':
            filter_query = ("(ef_filter.`field_id` = %(FieldID_{field_id})s "
                            "AND ef_filter.`value_ATTACH` IS NOT NULL) ").format(field_id=field_id)
            self.tokens["FieldID_{}".format(field_id)] = field_id
            
            if value=='true':
                self.where_field.append(filter_query)
            else:
                self.not_field.append(filter_query)

        
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

    def retrieveMutationData(self):
        '''
        Gather all mutation data, filtered by field and reference

        Filters are key_value pairs with the key formatted like:
        - MutationName
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
        self.not_field = []
        self.where_ref = []
        field_types = _map_field_types()
        
        for key in request.args:
            value = request.args[key]

            if key == 'MutationName':
                self.where_base.append("e.`name` LIKE CONCAT('%%', %(MutationName)s ,'%%') ")
                self.tokens['MutationName'] = request.args['MutationName']
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
        sql = _compose_query(self.where_base, self.where_field, self.not_field, self.where_ref)

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
        data = self.retrieveMutationData()

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
            row.append('\n'.join([str(p) if p is not None else '' for p in pubmed_ids]))

            for field in fields:
                field_id = field['id']
                if field_id in exp['fields']:
                    field_values = list(exp['fields'][field_id].values())
                    row.append('\n'.join([str(f) if f is not None else '' for f in field_values]))
                else:
                    row.append('')                    
            
            writer.writerow(row)
            
        return output.getvalue()
            
    
    def get(self):
        result = self.retrieveMutationData()
        return result

    @login_required
    def post(self):
        args = self.reqparse.parse_args()

        exp_name = args['name']

        ##Experiment
        sql = "INSERT INTO `experiments` (`name`) VALUES (%(exp_name)s)"
        cursor = self.db.cursor()
        cursor.execute(sql, {'exp_name': exp_name})
        exp_id = cursor.lastrowid
        cursor.close()

        ##Fields
        if args['fields']:
            field_types = _map_field_types()
            _edit_fields(exp_id, args['fields'], field_types, self.db)
                    
        ##References
        if args['references']:
            _edit_references(exp_id, args['references'], self.db)
                            
        self.db.commit()

        created = request.json
        created['id'] = exp_id
        return created, 201


class Mutation(CamelResource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()

        ##PUT arguments
        self.reqparse.add_argument('name', type = str, location = 'json')
        self.reqparse.add_argument('fields', type = dict, location = 'json')
        # self.reqparse.add_argument('references', type = list, location = 'json')

        super(Mutation, self).__init__()
    
    def get(self, id):
        where_base = ["e.`id` = %(id)s"]
        tokens = {'id': id}
        
        c = self.db.cursor(DictCursor)
        sql = _compose_query(where_base)
        print(sql)
        c.execute(sql, tokens)
        res = c.fetchall()
        c.close()
        field_types = _map_field_types()
        result = _compact(res, field_types, self.db)

        if len(result) > 0:
            return result
        else:
            return 'Unknown Mutation ID', 400
    
    @login_required
    def put(self, id):        
        ## Without authentication, the user can only make
        ## suggestions, but never overwrite an entry.

        ##TODO implement the suggestion idea        
        
        args = self.reqparse.parse_args()

        ##Experiment properties
        if args['name']:
            cursor = self.db.cursor()
            name = args['name']
            sql = "UPDATE `experiments` SET `name` = %(name)s WHERE `id` = %(id)s"
            cursor.execute(sql, {'id': id, 'name': name})
            cursor.close()

        ##Fields
        if args['fields']:
            field_types = _map_field_types()
            _edit_fields(id, args['fields'], field_types, self.db)
                    
        ##References
        if args['references']:
            _edit_references(id, args['references'], self.db)
                            
        self.db.commit()
        
        return "UPDATED", 204

    @login_required
    def delete(self, id):
        cursor = self.db.cursor()

        ## Get linked references
        sql = "SELECT `reference_id` FROM `experiments_references` WHERE `experiment_id` = %(id)s"
        cursor.execute(sql, {'id': id})
        refs = cursor.fetchall()
        ref_id_list = [ref[0] for ref in refs]
        
        sql = "DELETE FROM `experiments` WHERE `id` = %(id)s"
        cursor.execute(sql, {'id': id})

        ## Delete orphan references
        for ref_id in ref_id_list:
            sql = "SELECT * FROM `experiments_references` WHERE `reference_id` = %(ref_id)s"
            linkCount = cursor.execute(sql, {'ref_id': ref_id})

            if linkCount == 0:
                sql = "DELETE FROM `references` WHERE `id` = %(ref_id)s"
                cursor.execute(sql, {'ref_id': ref_id})

        ## Delete attachments
        upload_conf = config['uploads']
        target_path = Path(upload_conf['PATH'])
        target_exp_path = target_path.joinpath(str(id))
        shutil.rmtree(target_exp_path, ignore_errors=True)
                
        self.db.commit()
        cursor.close()
        
        return "DELETED", 204
