import requests as req
import click
import getpass
import sys

base_url = "http://localhost/CAMEL/"
api_url = base_url + "api"
auth_url = base_url + "auth"
exp_url = api_url + "/experiment"

def load_pids(pid_file):
    pids = []
    with open(pid_file) as input:
        for line in input:
            line = line.strip()
            if line:
                pids.append(int(line))
            else:
                pids.append(None)
    return pids

def get_auth(creds):
    auth_request = req.get(auth_url, auth=creds)
    if auth_request.status_code == 200:
        token = auth_request.headers['AuthToken']
    else:
        print(auth_request)
        print("Could not log in as CAMEL admin with account {}".format(creds[0]))
        sys.exit(1)
    
    
    ## Create the header we're going to send along
    auth_header = {'AuthToken': token}
    return auth_header


def update_references(pids, creds):
    auth_header = get_auth(creds)
    
    exps = req.get(exp_url).json()
    exp_nr = 0
    for exp in exps:
        print("Updating experiment {} - {}".format(exp['id'], exp['name']))        
        exp['references'][0]['pubmed_id'] = pids[exp_nr]
        exp_nr+=1
        update_url = exp_url + '/' + str(exp['id'])
        resp = req.put(update_url, json=exp, headers=auth_header)
        if resp.status_code != 204:
            print("Could not update: {}".format(resp.status_code))
            

            
@click.command()
@click.argument('pid_file',
                required = True,
                type = click.Path(exists=True)
)
@click.option('-u', '--user',
              help='CAMEL admin username'
)
@click.option('-p', '--password',
              help='CAMEL admin password'
)
def main(pid_file, user, password):
    """
    PID_FILE : list of PubmedIds, one per line, in the same order as the original experiments
    were imported.
    """
    pids = load_pids(pid_file)
    
    if not user:
        user = getpass.getuser()

    if not password:
        password = getpass.getpass()

    creds = (user, password)
    update_references(pids, creds)

if __name__ == '__main__':
    main()
