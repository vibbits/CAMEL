from flask_restful import request, reqparse
from MySQLdb.cursors import DictCursor
from flask_restful import reqparse
from Camel import CamelResource
from Camel import auth

class FieldList(CamelResource):

    def __init__(self):
        self.reqparse = reqparse.RequestParser()

        ##POST arguments
        self.reqparse.add_argument('title', required = True, type = str, location = 'json')
        self.reqparse.add_argument('unit', required = True, type = str, location = 'json')
        self.reqparse.add_argument('description', required = True, type = str, location = 'json')
        self.reqparse.add_argument('type_column', required = True, type = str, location = 'json')
        self.reqparse.add_argument('link', required = True, type = int, location = 'json')
        self.reqparse.add_argument('required', required = True, type = int, location = 'json')
        self.reqparse.add_argument('group', required = True, type = int, location = 'json')
        self.reqparse.add_argument('weight', required = True, type = int, location = 'json')
        self.reqparse.add_argument('group_id', required = True, type = int, location = 'json')

        super(FieldList, self).__init__()
        
    def retrieveFieldData(self):
        sql = ("SELECT `id`, `title`, `unit`, `description`, `type_column`, `link`, `required`, `weight`, `group`, `group_id` "
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


    def post(self):
        if not auth.is_authenticated():
            return "Admin only", 401
        
        sql = ("INSERT INTO `fields` (`title`, `unit`, `description`, `type_column`, `link`, `required`, `weight`, `group`, `group_id`) "
               "VALUES (%(title)s, %(unit)s, %(description)s, %(type_column)s, %(link)s, %(required)s, %(weight)s, %(group)s, %(group_id)s)")

        args = self.reqparse.parse_args()
        c = self.db.cursor()
        c.execute(sql, args)
        self.db.commit()
        c.close()
        
        return "Success"

    
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
