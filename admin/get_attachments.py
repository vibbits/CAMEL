'''
Short example of how to get the download URLs for attachment fields
'''

import requests as req

## Get the URL where attachments are hosted
## and the API URL
attach_url = "http://dev.bits.vib.be/CAMEL/api/attachment"
api_url = "http://dev.bits.vib.be/CAMEL/api"

## Get field info for eg. Mutation Data
field_api_url = api_url+"/field/Mutation Data"

field_info = req.get(field_api_url).json()
field_id = field_info['id']

## Retrieve data from eg. experiment 712
exp_id = 712
exp_api_url = api_url+"/experiment/"+str(exp_id)
exp_data = req.get(exp_api_url).json()

for attach in exp_data['fields'][str(field_id)].values():
    download_url = attach_url+"/{}/{}/{}".format(exp_id, field_id, attach)
    print(download_url)
    
