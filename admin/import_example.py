import requests as req

'''
This is a simple script to demonstrate the editting API 
of CAMEL. If you run it one line at a time, you can see
how different enitities are added, updated and removed.
At the end of the script, the db should be back in its original
state.

Request types:
'GET': retrieve one or more enities as described in the README
'POST': inserts a new experiment or field
'PUT': update an existing experiment or field given the id
'DELETE': remove an existing experiment, field or reference given the id

References can be added and updated as a part of an experiment.
Removing a field will automatically remove all data of that type, just like
removing an experiment will also delete its field data. Orphan references
(references that are not linked to any experiment anymore) are
automatically removed as well.

'''

## URLS
base_url = "https://dev.bits.vib.be/CAMEL/"
api_url = base_url + "api"
auth_url = base_url + "auth"

exp_url = api_url + "/experiment"
field_url = api_url + "/field"
ref_url = api_url + "/reference"

## Credentials
login = 'thpar'
password = ''

if not password:
    import getpass
    getpass.getpass()

## Get an authentication token
'''
All editting operations require a header containing a valid AuthToken.
A token stays valid for one day.
'''
auth_request = req.get(auth_url, auth=(login, password))
token = auth_request.headers['AuthToken']

## Create the header we're going to send along
auth_header = {'AuthToken': token}


## Add a new experiment
'''
Adding or updating an element needs a dict that mimics 
the JSON format like a GET request would return.

Field values key/value pairs that do not have a generated ID yet, use a 
random id that's pre-fixed with 'new_'.
'''
new_experiment = {
    'name': "A fresh experiment",  ## the only required attribute
    ## key value pairs with field id as key
    'fields': {
        '1': {
            'new_1': "My new species",
            'new_2': "Another new species"
            },
        '2': {
            'new_3': "The goal of this experiment"
            },
        '34': {
            'new_4': "The major outcome of this experiment can be described here"
            },
        '10': {
            'new_5': 0  ##no, there is NO changing environment
            }
        },
    ## list of linked references
    'references': [
        {
            ## By default, references need a reference ID and the complete reference data
            ## with __all reference fields__ (see get results) to do an UPDATE.
            ## This behaviour can be changed by the 'action' attribute: 'new' (post, without ref id)
            ## or 'link' or 'delete' (with existing ref id)
            'id': '11954',
            'action': 'link'  ## link existing paper to this experiment
        },
        {            
            'action': 'new',  ## a completely new paper
            'authors': "a list of authors goes here",
            'title': "this is the title of the new paper",
            'journal': 'Journal Abbr.',
            'year': '2019',
            'pages': '',
            'pubmed_id': '',
            'url': ''          
        }
        ]
    }

## Send the new experiment data
## It will be added to the database
## The JSON answer will be the same experiment, but with an assigned ID.
answer = req.post(exp_url, headers=auth_header, json=new_experiment).json()
exp_id = answer['id']
added_exp_url = exp_url + '/' + str(exp_id)

## Field value id's will not be assigned yet, until we request the complete object again
added_experiment = req.get(added_exp_url).json()

## Let's update the Species field. We only need the changing fields and the ids of their values.
species_value_ids = list(added_experiment['fields']['1'].keys())

update_experiment = {
    'fields': {
        '1': {
            species_value_ids[0]: 'We update this species',
            species_value_ids[1]: {'action': 'delete'}, ## we delete the second value
            'new_1': 'Adding yet another species'
            }
        }
    }


## Send the updates
req.put(added_exp_url, headers = auth_header, json=update_experiment)


## We can now delete this test experiment again.
## The 'new' paper will be removed with it. The existing paper
## will be unaffected.
req.delete(added_exp_url, headers=auth_header)


## In a more simple way, we could add a new field
new_field = {
    'title': "An extra field",
    'unit': "centimeters",
    'description': "This is a testing field",
    'type_column': 'value_VARCHAR', ## Content type. Can also be 'value_INT', 'value_DOUBLE','value_BOOL','value_TEXT'
    'link': 0, ## it should not be treated as URL
    'required': 0,  ## required field
    'group': 0,   ## boolean toggling a group of fields
    'weight': 900, ## order of fields in the table
    'group_id': None ## id of other field marked as 'group'
    }

answer = req.post(field_url, headers=auth_header, json=new_field).json()
field_id = answer['id']
added_field_url = field_url + '/' + str(field_id)

## Update the field (eg. make it required)
update_field = {
    'required': 1
    }

req.put(added_field_url, headers=auth_header, json=update_field)

## Delete this field again
req.delete(added_field_url, headers=auth_header)
