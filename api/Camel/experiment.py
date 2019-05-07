from flask_restful import Resource

class ExperimentList(Resource):
    def get(self):
        return {'msg': "Hello Experiment!"}



class Experiment(Resource):
    def get(self):
        return {'msg': "Hello Experiment!"}

