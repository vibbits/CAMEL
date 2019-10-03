'''
Add an attachment to an existing experiment.
In this example the attachment field has ID 36
'''

import requests as req

base_url = "http://localhost/CAMEL/"
api_url = base_url + "api"
auth_url = base_url + "auth"
exp_url = api_url + "/experiment"
attach_url = api_url + '/attachment'

##For editting the database, we need an authorization token
login = 'thpar'
password = ''

if not password:
    import getpass
    password=getpass.getpass()

auth_request = req.get(auth_url, auth=(login, password))
token = auth_request.headers['AuthToken']
auth_header = {'AuthToken': token}


##Say we want to add an attachment (a jpg in this folder) to experiment 717
local_file_name = "test_upload.jpg"
this_exp_url = exp_url+'/717'

##We upload the file to a temporary location on the server
attachment = {'file': open(local_file_name, 'rb')}
resp = req.post(attach_url, files=attachment, headers=auth_header)

##Get the temporary id of the upload
tmp_uuid = resp.json()['uuid']

##Set the attachment field to the tmp id and name the file
##The file will be moved to the correct location
dest_file_name = "attached_data.jpg"
attach_exp = {
    'fields': {
        '36': {
            'new_1': {
                'uuid': tmp_uuid,
                'filename': dest_file_name}
        }
    }
}
resp = req.put(this_exp_url, headers = auth_header, json=attach_exp)
if resp.ok:
    print("Upload successful")
else:
    print("Upload failed")
