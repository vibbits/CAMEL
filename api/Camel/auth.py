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
    if 'Authorization' in request.headers:
        token = request.headers['Authorization']
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
    

def stop_session():
    if 'Authorization' in request.headers:
        token = request.headers['Authorization']
        
        sql = "DELETE FROM `sessions` WHERE `token` = %(token)s"
        db = db_connect(config)
        c = db.cursor()
        c.execute(sql, {'token': token})
        db.commit()
        c.close()    
        db.close()
        return "Logged out"
    else:        
        return "Not logged in", 401

