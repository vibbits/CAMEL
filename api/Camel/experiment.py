from flask_restful import Resource

class Experiment(Resource):
    def get(self):
        return {'msg': "Hello Experiment!"}

