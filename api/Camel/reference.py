from flask_restful import request
from MySQLdb.cursors import DictCursor
from Camel import CamelResource
from Camel.auth import is_authenticated


class ReferenceList(CamelResource):
    def get(self):
        sql = "SELECT * FROM `references` ORDER BY `year`"

        c = self.db.cursor(DictCursor)
        c.execute(sql)
        rows = c.fetchall()
        c.close()
        return rows

    
class Reference(CamelResource):
    def get(self, id):
        sql = "SELECT * FROM `references` WHERE `id` = %(ref_id)s"

        c = self.db.cursor(DictCursor)
        c.execute(sql, {'ref_id': id})
        res = c.fetchone()
        c.close()
        return res

        
    def delete(self, id):
        if not is_authenticated():
            return "Admin only", 401

        sql = "DELETE FROM `references` WHERE `id` = %(ref_id)s"

        c = self.db.cursor()
        c.execute(sql, {'ref_id': id})        
        c.close()
        self.db.commit()

        return "Reference deleted", 204
