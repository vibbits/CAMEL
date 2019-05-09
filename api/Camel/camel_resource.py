from flask_restful import Resource
import Camel as app

class CamelResource(Resource):
    def __init__(self):
        self.db = app.get_db()
        super(Resource, self).__init__()
