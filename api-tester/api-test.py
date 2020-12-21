import json
import requests
import argparse
import getpass
#
# Setup the parser
#
parser = argparse.ArgumentParser()
parser.add_argument("base_url", help="The base URL to call")
parser.add_argument("username", help="Triad username")
parser.add_argument("org_label", help="The ORG label")
parser.add_argument('-e', '--endpoints', nargs="*", help="A space separated list of REST endpoints to append to the URL")

args = parser.parse_args()
#
# Setup the program arguments
# 
protocol = "http"
base_url = protocol + "://" + args.base_url
username = args.username
org = args.org_label
endpoints = []

if(args.endpoints):
    endpoints = args.endpoints
else:
    endpoints = [
    "/device-api/v1/devices",
    "/location-api/v1/locations",
    "/ont-api/v1/onts",
    "/phone-api/v1/phones",
    "/service-api/v1/services",
    "/subscriber-api/v1/subscribers",
    "/work-queue-api/v1/controller-work"
    ]
#
# Do the special to get the password prompt
#
password = getpass.getpass(prompt='Password: ', stream=None) 

#
# Will fetch and return a token from the auth-api at the base_url
#  
def get_token():
    headers = {'Content-Type': 'application/json', 'accept': 'application/json'}
    api_url = base_url + "/auth-api/auth"
    print("Getting token from " + api_url)
    args={"username":username,"password":password,"org":org}
    response = requests.post(api_url, headers=headers, json=args)

    if response.status_code == 200:
        token_obj =  json.loads(response.content.decode('utf-8'))
        return token_obj['jwt']
    else:
        print(response)
        return None

# 
# Call the given REST endpoint with the provided token and return an object count
#
def call_rest_endpoint(endpoint, token):
    api_url = base_url + endpoint
    headers = {'Authorization': 'Bearer ' + token, 'accept': 'application/hal+json'}
    response = requests.get(api_url, headers=headers)

    if response.status_code == 200:
        response_obj =  json.loads(response.content.decode('utf-8'))
        print("Found " + str(response_obj['page']['totalElements']) + " objects for the endpoint " + endpoint)
    else:
        print("Resonse code: " + str(response.status_code) + " for " + endpoint)
        return None


token = get_token()
print("Got a token: " + token)


if(token is None):
    print("No token found")
else:
    if(len(endpoints) > 0):
        for endpoint in endpoints:
            call_rest_endpoint(endpoint, token)



