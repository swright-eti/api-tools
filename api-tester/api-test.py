import json
import requests
import argparse
import getpass

parser = argparse.ArgumentParser()
parser.add_argument("base_url")
parser.add_argument("username")
parser.add_argument("org_label")
args = parser.parse_args()


base_url = args.base_url
username = args.username
org = args.org_label

password = getpass.getpass(prompt='Password: ', stream=None) 

token = None

def get_token():
    headers = {'Content-Type': 'application/json', 'accept': 'application/json'}
    api_url = base_url + "/auth-api/auth"
    print("Getting token from:" + api_url)
    args={"username":username,"password":password,"org":org}
    response = requests.post(api_url, headers=headers, json=args)

    if response.status_code == 200:
        token_obj =  json.loads(response.content.decode('utf-8'))
        return token_obj['jwt']
    else:
        print(response)
        return None

def get_data(endpoint):
    api_url = base_url + endpoint
    headers = {'Authorization': 'Bearer ' + token, 'accept': 'application/hal+json'}
    response = requests.get(api_url, headers=headers)

    if response.status_code == 200:
        response_obj =  json.loads(response.content.decode('utf-8'))
        print("Found " + str(response_obj['page']['totalElements']) + " objects for the endpoint " + endpoint)
    else:
        print("Resonse code: " + str(response.status_code) + " for " + endpoint)
        return None


endpoints = [
    "/device-api/v1/devices",
    "/location-api/v1/locations",
    "/ont-api/v1/onts",
    "/phone-api/v1/phones",
    "/service-api/v1/services",
    "/subscriber-api/v1/subscribers",
    "/work-queue-api/v1/controller-work"
]

token = get_token()

if token is None:
    print("Could not get token")
else: 
    for endpoint in endpoints:
        get_data(endpoint)



