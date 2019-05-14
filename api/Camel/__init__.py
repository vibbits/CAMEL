from flask import Flask, make_response
from flask_restful import Api, Resource

import sys
import os
import MySQLdb

## Load configuration
import configparser as cp
config = cp.ConfigParser()
package_path = os.path.dirname(os.path.abspath(__file__))
app_path = os.path.dirname(os.path.dirname(package_path))
config_path = os.path.join(app_path, 'camel.conf')
config.read(config_path)


## Database connection in Resource parent class
class CamelResource(Resource):
    def db_connect(self):
        db_conf = config['database']
        try:
            self.db = MySQLdb.connect(host=db_conf['HOST'],
                                 user=db_conf['USER'],
                                 passwd=db_conf['PASSWORD'],
                                 db=db_conf['NAME'],
                                 charset='utf8'
            )
        except:
            print("Can't connect to database")
            sys.exit(1)

        return self.db
        
    def __init__(self):
        self.db_connect()
        super(Resource, self).__init__()

    

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

## Export

@app.route('/export')
def export_csv():
    expList = ExperimentList()
    csv = expList.csv()

    response = make_response(csv)
    response.headers["Content-Disposition"] = "attachment; filename=camel_export.csv"
    return response
