from flask import Flask, request, make_response
import sys
import os
import logging
import MySQLdb

logging.basicConfig(stream=sys.stderr)
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))


## Load configuration
import configparser as cp
config = cp.ConfigParser()
package_path = os.path.dirname(os.path.abspath(__file__))
app_path = os.path.dirname(package_path)
config_path = os.path.join(app_path, 'camel.conf')
config.read(config_path)


application = Flask(__name__)

def db_connect():
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

def start_session():
    import uuid
    token = str(uuid.uuid4())
    sql = "INSERT INTO `sessions` (`token`, `created`) VALUES (%(token)s, NOW())"
    db = db_connect()
    c = db.cursor()
    c.execute(sql, {'token': token})
    db.commit()
    c.close()    
    db.close()
    return token


@application.route('/')
def authenticate():
    token = start_session()
    msg = "Authentication successful"
    response = make_response(msg)
    response.headers['Authorization'] = token
    return response

@application.route('/logout')
def logout():
    if 'Authorization' in request.headers:
        token = request.headers['Authorization']

        ## Delete current token and clean up expired tokens.
        sql = "DELETE FROM `sessions` WHERE `token` = %(token)s OR `created` < NOW() - INTERVAL 1 DAY"
        db = db_connect()
        c = db.cursor()
        c.execute(sql, {'token': token})
        db.commit()
        c.close()    
        db.close()
        return "Logged out"
    else:        
        return "Not logged in", 401



if __name__ == '__main__':
    application.run(debug=True)
