from Camel import config
from flask import request, make_response
import sys
import MySQLdb

def db_connect(config):
    db_conf = config['database']
    try:
        db = MySQLdb.connect(host=db_conf['HOST'],
                             user=db_conf['USER'],
                             passwd=db_conf['PASSWORD'],
                             db=db_conf['NAME'],
                             charset='utf8'
        )
    except:
        print("Can't connect to database")
        sys.exit(1)

    return db

def is_authenticated():    
    if 'AuthToken' in request.headers:
        token = request.headers['AuthToken']
    else:
        return False
    
    db = db_connect(config)
    sql = "SELECT `token` from `sessions` WHERE `token` = %(token)s"
    c = db.cursor()
    c.execute(sql, {'token': token})
    rows = c.fetchall()    
    c.close()
    db.close()

    return len(rows)==1
    
