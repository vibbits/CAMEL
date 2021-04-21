import sys
import os
import pathlib

from flask import Flask, make_response
from flask_restful import Api, Resource

import MySQLdb

## Load configuration
import configparser as cp
config = cp.ConfigParser()
package_path = os.path.dirname(os.path.abspath(__file__))
app_path = os.environ.get('APP_PATH') or os.path.dirname(os.path.dirname(package_path))
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

    
from Camel.auth import Auth, Logout
from Camel.experiment import Experiment, ExperimentList
from Camel.field import Field, FieldList
from Camel.reference import Reference, ReferenceList
from Camel.attachment import Attachment
from Camel.pubmed import PubMed
from Camel.mutation import Mutation, MutationList

## Init Flask App
app = Flask(__name__)
api = Api(app)

## Define routing
api.add_resource(Auth, '/auth/')
api.add_resource(Logout, '/auth/logout')
api.add_resource(ExperimentList, '/experiment')
api.add_resource(Experiment, '/experiment/<int:id>')
api.add_resource(MutationList, '/mutation')
api.add_resource(Mutation, '/mutation/<int:id>')
api.add_resource(FieldList, '/field')
api.add_resource(Field, '/field/<string:id>')
api.add_resource(ReferenceList, '/reference')
api.add_resource(Reference, '/reference/<int:id>')
api.add_resource(Attachment, '/attachment')
api.add_resource(PubMed, '/pubmed/<int:pubmed_id>')

## Export

@app.route('/export')
def export_csv():
    expList = ExperimentList()
    csv = expList.csv()

    response = make_response(csv)
    response.headers["Content-Disposition"] = "attachment; filename=camel_export.csv"
    return response
