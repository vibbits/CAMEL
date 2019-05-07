from flask import Flask
from flask_restful import Api
import configparser
import sys
import os
import MySQLdb

from Camel.experiment import Experiment, ExperimentList
from Camel.field import Field, FieldList

## Init Flask App
app = Flask(__name__)
api = Api(app)

## Define routing
api.add_resource(ExperimentList, '/experiment')
api.add_resource(Experiment, '/experiment/<int:id>')
api.add_resource(FieldList, '/field')
api.add_resource(Field, '/field/<string:id>')

## Load configuration
config = configparser.ConfigParser()
package_path = os.path.dirname(os.path.abspath(__file__))
app_path = os.path.dirname(os.path.dirname(package_path))
config_path = os.path.join(app_path, 'camel.conf')
config.read(config_path)


## Database connection
def get_db():
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
