from flask_restful import Resource, request
from MySQLdb.cursors import DictCursor
import Camel as app

class ExperimentList(Resource):
    def __init__(self):
        self.db = app.get_db()
        super(ExperimentList, self).__init__()
    
    def get(self):
               
        where = []
        tokens = {}
        sql = ("SELECT e.`id` AS `experiment_id`, e.`name`, "
               "f.`id` AS `field_id`, f.`title` AS `field_title`, f.`weight`, "
               "CONCAT_WS('-',ef.`value_INT`,ef.`value_VARCHAR`,ef.`value_DOUBLE`,ef.`value_BOOL`,ef.`value_TEXT`) AS `value` "
               "FROM `experiments` e "
               "LEFT JOIN `experiments_fields` ef ON e.`id` = ef.`experiment_id` "
               "LEFT JOIN `fields` f ON ef.`field_id` = f.`id` ")

        filter_b = ("e.`id` IN (SELECT ef_filter.`experiment_id` "
                    "FROM `experiments_fields` ef_filter "
                    "WHERE ")
        filter_e = ") "
            
        order = " ORDER BY e.`id`, f.`weight`"

        ##map all field types
        fields_sql = "SELECT `id`, `type_column` FROM `fields`"
        c = self.db.cursor(DictCursor)
        c.execute(fields_sql)
        res = c.fetchall()
        c.close()
        
        field_types = {}
        for row in res:
            field_types[row['id']] = row['type_column'].split('_')[1]

        ##Filters
        ##Name filter
        if 'ExperimentName' in request.args:
            where.append("e.`name` like CONCAT('%', %(ExperimentName)s ,'%') ")
            tokens['ExperimentName'] = request.args['ExperimentName']

        ##Field filters
        for key in request.args:
            value = request.args[key]
            key_parts = key.split('_')
            if len(key_parts) == 2:
                field_id = key_parts[1]
            else:
                field_id = key

            ##Only process filters on field nr here
            if field_id.isnumeric():
                field_id = int(field_id)
                field_type = field_types[field_id]
            else:
                continue
            
            if field_type == 'VARCHAR' or field_type == 'TEXT':
                filter_query = ("(ef_filter.`field_id` = %(FieldID_{field_id})s AND ef_filter.`value_{field_type}` "
                                "LIKE CONCAT('%%', %(FieldValue_{field_id})s ,'%%')) ").format(field_id=field_id, field_type=field_type)

                tokens["FieldID_{}".format(field_id)] = field_id
                tokens["FieldValue_{}".format(field_id)] = value
                where.append(filter_b + filter_query + filter_e)
                
            elif field_type == 'INT' or field_type == 'DOUBLE':
                filter_query = "(ef_filter.`field_id` = %(FieldID_{field_id})s ".format(field_id=field_id)
                tokens["FieldID_{}".format(field_id)] = field_id
                
                if 'min_'+str(field_id) in request.args:
                    min_value = request.args['min_'+str(field_id)]
                    filter_query+= "AND ef_filter.`value_{field_type}` >= %(FieldMinValue_{field_id})s ".format(field_type=field_type, field_id=field_id)
                    tokens["FieldMinValue_{}".format(field_id)] = min_value
                if 'max_'+str(field_id) in request.args:
                    max_value = request.args['max_'+str(field_id)]
                    filter_query+= "AND ef_filter.`value_{field_type}` <= %(FieldMaxValue_{field_id})s ".format(field_type=field_type, field_id=field_id)
                    tokens["FieldMaxValue_{}".format(field_id)] = max_value

                filter_query+= ") "
                where.append(filter_b + filter_query + filter_e)
                
            elif request.args == 'BOOL':
                bool_value = 1 if value=='true' else 0
                filter_query = ("(ef_filter.`field_id` = %(FieldID_{field_id})s "
                                "AND ef_filter.`value_BOOL` = %(FieldValue_{field_id})s) ").format(field_id=field_id)
                tokens["FieldID_{}".format(field_id)] = field_id
                tokens["FieldValue_{}".format(field_id)] = bool_value
                where.append(filter_b + filter_query + filter_e)

                
        if len(where) > 0:
            sql+=" WHERE "+' AND '.join(where)
            
        sql+= order

        c = self.db.cursor(DictCursor)
        c.execute(sql, tokens)
        res = c.fetchall()
        c.close()

        ##Combine all field/value results into one entry per experiment
        summary = {}
        for entry in res:
            experiment_id = entry['experiment_id']
            if experiment_id not in summary:
                summary[experiment_id] = {}
                summary[experiment_id]['name'] = entry['name']
                summary[experiment_id]['fields'] = {}

            field_id = entry['field_id']
            field_value = entry['value']
            
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

            c = self.db.cursor(DictCursor)
            c.execute(sql, {'ID': exp_id})
            res = c.fetchall()
            c.close()
                                            
            exp['references'] = res            
            result.append(exp)

        return result


class Experiment(Resource):
    def get(self):
        return {'msg': "Hello Experiment!"}

            # } else {
            #     $where[]= " e.`id` = :ID";
            #     $tokens[':ID'] = $id;

            #     $sql.=" WHERE ".implode(" AND ", $where);
            #     $qry = $this->db->prepare($sql);
            #     $qry->setFetchMode(PDO::FETCH_ASSOC);
            #     $qry->execute($tokens);
            #     $res = $qry->fetchAll();
            # }

