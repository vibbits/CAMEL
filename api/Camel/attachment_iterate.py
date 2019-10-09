'''
Add an attachment to an existing experiment.
In this example the attachment field has ID 36
'''

import requests as req

base_url = "http://dev.bits.vib.be/CAMEL/"
api_url = base_url + "api"
auth_url = base_url + "auth"
exp_url = api_url + "/experiment"
attach_url = api_url + '/attachment'
num = 0

##For editting the database, we need an authorization token
login = ''
password = ''

if not password:
    import getpass
    password=getpass.getpass()

auth_request = req.get(auth_url, auth=(login, password))
token = auth_request.headers['AuthToken']
auth_header = {'AuthToken': token}

import re
import os

##iterate over all files in certain directory. As long as they are xlsx, csv, txt, or csv, they will be uploaded. They do have to contain the number of the experiment
##furthermore, they can only contain the number of the experiment in their name, no other numbers

for filename in os.listdir("C:/Python27/data"):
    if filename.endswith(".xlsx") or filename.endswith(".txt") or filename.endswith(".tsv") or filename.endswith(".csv"): 
       local_file_name = filename
       str1 = filename
       num=re.findall('\d+', str1 )
       number = num[0]
       this_exp_url = exp_url+'/'+number
       attachment = {'file': open('C:/Python27/data/'+local_file_name, 'rb')}
       resp = req.post(attach_url, files=attachment, headers=auth_header)
       tmp_uuid = resp.json()['uuid']
		
       dest_file_name = "attached_data.xlsx"
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
       continue
    else:
       continue


##Say we want to add an attachment (a jpg in this folder) to experiment 717
##local_file_name = 'C:\Python27\BurkMA.xlsx'
##this_exp_url = exp_url+'/15'

##We upload the file to a temporary location on the server
##attachment = {'file': open(local_file_name, 'rb')}
##resp = req.post(attach_url, files=attachment, headers=auth_header)

##Get the temporary id of the upload
##tmp_uuid = resp.json()['uuid']

##Set the attachment field to the tmp id and name the file
##The file will be moved to the correct location
##dest_file_name = "attached_data.xlsx"
##attach_exp = {
  ##  'fields': {
    ##    '36': {
      ##      'new_1': {
        ##        'uuid': tmp_uuid,
          ##      'filename': dest_file_name}
        ##}
    ##}
##}
##resp = req.put(this_exp_url, headers = auth_header, json=attach_exp)
##if resp.ok:
##    print("Upload successful")
##else:
##    print("Upload failed")
