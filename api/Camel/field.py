from flask_restful import Resource

class Field(Resource):
    def get(self):
        return {'msg': "Hello Field!"}

