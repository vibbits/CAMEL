from flask import Flask
from flask_restful import Api
import configparser
import sys
import MySQLdb

from Camel.experiment import Experiment
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
config.read('../camel.conf')


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
