import pytest
import requests

ALL_MUTATION_ENDPOINT = 'http://localhost:8888/api/mutations'
SINGLE_MUTATION_ENDPOINT = 'http://localhost:8888/api/mutation/'

class MutationsTest(pytest):

    def post_mutation_test(self):
        True

    def get_all_mutations_test(self):
        response = requests.get(ALL_MUTATION_ENDPOINT)
        assert response.status_code == 200

    def get_single_mutation_test(self):
        experiment_id = '784'
        response = requests.get(SINGLE_MUTATION_ENDPOINT + experiment_id)
        assert response.status_code == 200

    def update_mutation_test(self):
        True

    def export_csv_test(self):
        True

    def delete_mutation_test(self):
        True
