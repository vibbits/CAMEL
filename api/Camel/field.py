from pathlib import Path
import shutil

from flask_restful import request, reqparse
from MySQLdb.cursors import DictCursor

from Camel import CamelResource, config
from Camel.auth import login_required

class FieldList(CamelResource):

    def __init__(self):
        self.reqparse = reqparse.RequestParser()

        ##POST arguments
        self.reqparse.add_argument('title', required = True, type = str, location = 'json')
        self.reqparse.add_argument('unit', required = True, type = str, location = 'json')
        self.reqparse.add_argument('description', required = True, type = str, location = 'json')
        self.reqparse.add_argument('type_column', required = True, type = str, location = 'json')
        self.reqparse.add_argument('options', required = True, type = str, location = 'json')
        self.reqparse.add_argument('link', required = True, type = int, location = 'json')
        self.reqparse.add_argument('required', required = True, type = int, location = 'json')
        self.reqparse.add_argument('group', required = True, type = int, location = 'json')
        self.reqparse.add_argument('weight', required = True, type = int, location = 'json')
        self.reqparse.add_argument('group_id', required = True, type = int, location = 'json')

        super(FieldList, self).__init__()
        
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


    @login_required
    def post(self):
        sql = ("INSERT INTO `fields` (`title`, `unit`, `description`, `type_column`, `options`, `link`, `required`, `weight`, `group`, `group_id`) "
               "VALUES (%(title)s, %(unit)s, %(description)s, %(type_column)s, %(options)s, %(link)s, %(required)s, %(weight)s, %(group)s, %(group_id)s)")

        args = self.reqparse.parse_args()
        c = self.db.cursor()
        c.execute(sql, args)
        newid = c.lastrowid
        self.db.commit()
        c.close()

        args['id'] = newid
        return args, 201

    
class Field(CamelResource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()

        ##PUT arguments
        self.reqparse.add_argument('title', type = str, location = 'json')
        self.reqparse.add_argument('unit', type = str, location = 'json')
        self.reqparse.add_argument('description', type = str, location = 'json')
        self.reqparse.add_argument('options', type = str, location = 'json')
        self.reqparse.add_argument('link', type = int, location = 'json')
        self.reqparse.add_argument('required', type = int, location = 'json')
        self.reqparse.add_argument('group', type = int, location = 'json')
        self.reqparse.add_argument('weight', type = int, location = 'json')
        self.reqparse.add_argument('group_id', type = int, location = 'json')

        ##Optional GET argument
        self.reqparse.add_argument('timeline', type = int, help = 'timeline is an optional flag [0|1]', location= 'args')
        
        super(Field, self).__init__()
    
    
    def get(self, id):
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

    @login_required
    def put(self, id):
        sql = "SELECT count(*) FROM `fields` WHERE `id` = %(id)s"
        c = self.db.cursor()
        c.execute(sql, {'id': id})
        res = c.fetchone()
        c.close()
        if res[0] != 1:
            return "No such field"

        args = self.reqparse.parse_args()
        if request.json:
            sql = "UPDATE `fields` SET "
            updates = []
            for arg_key in request.json:
                if arg_key in args:
                    updates.append("`{arg_key}` = %({arg_key})s ".format(arg_key=arg_key))
            sql+=', '.join(updates)
            sql+="WHERE id = %(id)s"
            c = self.db.cursor()
            tokens = args
            tokens['id'] = id
            c.execute(sql, tokens)
            self.db.commit()
            c.close()
            
        return "Update succesful", 204
        
    @login_required
    def delete(self, id):
        ## Does field exist?
        sql = "SELECT `id`, `type_column` FROM `fields` WHERE `id` = %(id)s"
        c = self.db.cursor()
        c.execute(sql, {'id': id})
        res = c.fetchall()

        if len(res) != 1:
            return "No such field"
        else:
            type_column = res[0][1]
                
        ## Clean up ATTACH field
        if type_column == 'value_ATTACH':
            upload_conf = config['uploads']            
            upload_path = Path(upload_conf['PATH'])
            sql = "SELECT `experiment_id` FROM `experiments_fields` WHERE `field_id` = %(id)s"
            c.execute(sql, {'id': id})
            res = c.fetchall()
            for row in res:
                exp_id = row[0]
                attachment_dir = upload_path.joinpath(str(exp_id), str(id))
                shutil.rmtree(attachment_dir, ignore_errors=True)

        ## Delete from db
        sql = "DELETE FROM `fields` WHERE `id` = %(id)s"

        c.execute(sql, {'id': id})

        self.db.commit()
        c.close()

        return "Field deleted", 204
    
