from flask_restful import request
from MySQLdb.cursors import DictCursor
from Camel import CamelResource
from Camel.auth import login_required


class ReferenceList(CamelResource):
    def get(self):
        sql = "SELECT * FROM `references` ORDER BY `year`, `title`"

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

        
    @login_required
    def delete(self, id):
        sql = "DELETE FROM `references` WHERE `id` = %(ref_id)s"

        c = self.db.cursor()
        c.execute(sql, {'ref_id': id})        
        c.close()
        self.db.commit()

        return "Reference deleted", 204
