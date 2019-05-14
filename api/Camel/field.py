from flask_restful import request, reqparse
from MySQLdb.cursors import DictCursor
from Camel import CamelResource

class FieldList(CamelResource):
    def retrieveFieldData(self):
        sql = ("SELECT `id`, `title`, `unit`, `description`, `type_column`, `options`, `link`, `required`, `weight`, `group`, `group_id` "
               "FROM `fields` "
               "ORDER BY `weight`")

        c = self.db.cursor(DictCursor)
        c.execute(sql)
        rows = c.fetchall()
        c.close()
        return rows
    
    def get(self):        
        rows = self.retrieveFieldData()
        return rows
        
class Field(CamelResource):
        
    def get(self, id):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('timeline', type = int, help = 'timeline is an optional flag [0|1]')
        self.reqparse.parse_args()
                
        sql = ("SELECT `id`, `title`, `unit`, `type_column` "
               "FROM `fields` ")

        tokens = {}
        if id.isnumeric():
            sql += "WHERE `id` = %(id)s"
            tokens['id'] = id
        else:
            sql += "WHERE `title` = %(title)s"
            tokens['title'] = id

        c = self.db.cursor(DictCursor)
        c.execute(sql, tokens)
        field_props = c.fetchone()
        c.close()
        
        type_col = field_props['type_column']

        if 'timeline' not in request.args or not request.args['timeline'] == '1':
            sql = ("SELECT ef.`{type_col}` value, COUNT(*) number "
                   "FROM `experiments_fields` ef "
                   "WHERE ef.`field_id` = %(field_id)s "
                   "GROUP BY `value` "
                   "ORDER BY `number` DESC").format(type_col=type_col)
        
        else:
            sql = ("SELECT ef.`{type_col}` value, r.`year`, COUNT(*) number "
                   "FROM `experiments_fields` ef "
                   "JOIN `experiments_references` er ON er.`experiment_id` = ef.`experiment_id` "
                   "JOIN `references` r ON r.`id` = er.`reference_id` "
                   "WHERE ef.`field_id` = %(field_id)s "
                   "GROUP BY `value`, `year` "
                   "ORDER BY `year`").format(type_col=type_col)

        tokens = {}
        tokens['field_id'] = field_props['id'];

        c = self.db.cursor(DictCursor)        
        c.execute(sql, tokens)
        field_stats = c.fetchall()
        field_props['values'] = field_stats;
        c.close()                
                
        return field_props
