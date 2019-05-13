from flask_restful import request
from MySQLdb.cursors import DictCursor
from Camel import CamelResource

def _compose_query(where_base = [], where_field = [], where_ref = []):
    '''
    Compose the SQL query to fetch a filtered list of experiments

    :param where_base: list of WHERE statements for main query
    :param where_field: list of WHERE statements for experiment_fields sub_query
    :param where_ref: list of WHERE statements for references_fields sub_query
    '''
    base = ("SELECT e.`id` AS `experiment_id`, e.`name`, "
           "f.`id` AS `field_id`, f.`title` AS `field_title`, f.`weight`, "
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

    :return a list a dictionaries, one per experiment 
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
            summary[experiment_id]['fields'][field_id] = []

        summary[experiment_id]['fields'][field_id].append(field_value)

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

def _map_field_types(db):
    '''
    :return a mapping of field id's to field type (VARCHAR, TEXT, INT, BOOL)
    '''
    fields_sql = "SELECT `id`, `type_column` FROM `fields`"
    c = db.cursor(DictCursor)
    c.execute(fields_sql)
    res = c.fetchall()
    c.close()
        
    field_types = {}
    for row in res:
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
            
    def get(self):               
        self.tokens = {}                        
        
        ##Filters
        ##Name filter
        self.where_base = []
        if 'ExperimentName' in request.args:
            self.where_base.append("e.`name` LIKE CONCAT('%%', %(ExperimentName)s ,'%%') ")
            tokens['ExperimentName'] = request.args['ExperimentName']

        ##Field filters
        self.where_field = []
        self.where_ref = []
        field_types = _map_field_types(self.db)
        
        for key in request.args:
            value = request.args[key]
            
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


class Experiment(CamelResource):
    def get(self, id):
        where_base = ["e.`id` = %(id)s"]
        tokens = {'id': id}
        
        c = self.db.cursor(DictCursor)
        sql = _compose_query(where_base)
        c.execute(sql, tokens)
        res = c.fetchall()
        c.close()
        field_types = _map_field_types(self.db)
        result = _compact(res, field_types, self.db)
        
        return result[0]
    
