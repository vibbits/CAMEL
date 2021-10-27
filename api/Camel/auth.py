import sys
from pathlib import Path
from functools import wraps

import bcrypt
import MySQLdb

from Camel import app_path, config, CamelResource
from flask import request, make_response

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

def login_required(endpoint):
    @wraps(endpoint)
    def wrapped_endpoint(self, *args, **kwargs):
        unauthorised = ('Unauthorized', 401, {
            'WWW-Authenticate': 'Basic realm="Login Required"'
        })

        if 'Authheader' not in request.headers:
            return unauthorised

        token = request.headers['Authheader']
        db = db_connect(config)
        sql = "SELECT `token` from `sessions` WHERE `token` = %(token)s"
        c = db.cursor()
        c.execute(sql, {'token': token})
        rows = c.fetchall()
        c.close()
        db.close()

        if len(rows) == 0:
            return unauthorised

        return endpoint(self, *args, **kwargs)

    return wrapped_endpoint

def start_session(db):
    import uuid
    token = str(uuid.uuid4())
    sql = "INSERT INTO `sessions` (`token`, `created`) VALUES (%(token)s, NOW())"
    c = db.cursor()
    c.execute(sql, {'token': token})
    db.commit()
    c.close()    
    return token


def cleanup_tokens(db):
    c = db.cursor()
    sql = "DELETE FROM `sessions` WHERE `created` < NOW() - INTERVAL 1 DAY"
    c.execute(sql)
    db.commit()
    c.close()

    
class Auth(CamelResource):
    def __init__(self):
        with open(Path(app_path) / '.htpasswd') as passwd:
            self.users = dict([tuple(entry.strip().split(':')) for entry in passwd.readlines()])

    def authenticate(self):
        auth = request.authorization
        if not (auth and bcrypt.checkpw(auth.password.encode('utf-8'), self.users.get(auth.username).encode('utf-8'))):
            return ('Unauthorized', 401, {
                'WWW-Authenticate': 'Basic realm="Login Required"'
            })

        db = db_connect(config)
        cleanup_tokens(db)
        token = start_session(db)
        db.close()

        msg = "Authentication successful"
        response = make_response(msg)
        response.headers['AuthToken'] = token
        return response
    
    def get(self):
        return self.authenticate()


class Logout(CamelResource):
    @login_required
    def get(self):
        token = request.headers['AuthToken']
        
        db = db_connect(config)
        c = db.cursor()
        sql = "SELECT * FROM `sessions` WHERE `token` = %(token)s"
        c.execute(sql, {'token': token})
        rows = c.fetchall()

        ## Delete current token
        sql = "DELETE FROM `sessions` WHERE `token` = %(token)s"
        c.execute(sql, {'token': token})
        db.commit()
        c.close()
        cleanup_tokens(db)
        db.close()
        return "Logged out"

