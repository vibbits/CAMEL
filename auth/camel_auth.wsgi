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
print(config_path)
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
    sql = "INSERT INTO `sessions` (`token`) VALUES (%(token)s)"
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
    msg = "Authentication successful: {}".format(token)
    response = make_response(msg)
    return msg


if __name__ == '__main__':
    application.run(debug=True)
