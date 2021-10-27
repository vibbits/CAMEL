import unittest
import requests
import pandas as pd
import json

ALL_MUTATION_ENDPOINT = 'http://localhost:8888/api/mutations'
SINGLE_MUTATION_ENDPOINT = 'http://localhost:8888/api/mutation'
AUTH_ENDPOINT = 'http://localhost:8888/api/auth/'
USER = 'admin'
PASS = 'password'

class TestMutations(unittest.TestCase):

    def test_post_mutation(self):
        # Get authorization
        auth_request = requests.get(AUTH_ENDPOINT, auth=(USER, PASS))
        auth_header = {'Authheader': auth_request.headers['AuthToken']}

        # Given payload (pandas DF) and an experiment_id
        df = pd.read_csv("Files/test_mutations.csv")
        new_mutations = df.to_dict()
        # Post payload DF to mutation endpoint
        response = requests.post(SINGLE_MUTATION_ENDPOINT, headers=auth_header, json=json.dumps(new_mutations))

        # Response = 200
        assert response.status_code == 200

    def test_get_all_mutations(self):
        response = requests.get(ALL_MUTATION_ENDPOINT)
        assert response.status_code == 200

    def test_get_single_mutation(self):
        experiment_id = '784'
        response = requests.get(SINGLE_MUTATION_ENDPOINT + '/' + experiment_id)
        assert response.status_code == 200

    def test_update_mutation(self):
        True

    def test_export_csv(self):
        True

    def test_delete_mutation(self):
        True
