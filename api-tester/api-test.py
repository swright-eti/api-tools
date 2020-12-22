import json
import requests
import argparse
import getpass
import re
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
base_url = args.base_url
username = args.username
org = args.org_label

#
# Do the special to get the password prompt
#
password = getpass.getpass(prompt='Password: ', stream=None) 

#
# Will fetch and return a token from the auth-api at the base_url
#  
def get_token(endpoint):
    headers = {'Content-Type': 'application/json', 'accept': 'application/json'}
    print("Getting token from " + endpoint)
    args={"username":username,"password":password,"org":org}
    response = requests.post(endpoint, headers=headers, json=args)

    if response.status_code == 200:
        token_obj =  json.loads(response.content.decode('utf-8'))
        print("Got a token: " + token_obj['jwt'])
        return token_obj['jwt']
    else:
        print(response)
        return None

# 
# Call the given REST endpoint with the provided token and return an object count
#
def call_rest_endpoint(endpoint, token):
    headers = {'Authorization': 'Bearer ' + token, 'accept': 'application/hal+json'}
    response = requests.get(endpoint, headers=headers)

    if response.status_code == 200:
        response_obj =  json.loads(response.content.decode('utf-8'))
        print("Found " + str(response_obj['page']['totalElements']) + " objects for the endpoint " + endpoint)
    else:
        print("Resonse code: " + str(response.status_code) + " for " + endpoint)
        return None
#
# If using kubefwd then this function will extract all the service names from the /etc/hosts file
#
def get_services_from_etc_hosts():
    services = []
    with open('/etc/hosts') as hosts:
        for line in hosts.readlines():
            res = re.search(r'^[0-9.]+\W+([a-z]+-api-service)', line) 
            if res:
                services.append(res.group(1))
    return services

#
# Build a dict of REST urls to K8s services names
def build_endpoint_dict():
    endpoints = {}
    if base_url == 'kubefwd':
        services = get_services_from_etc_hosts()
        for service in services:
            res = re.search(r'^(\w+)-(\w+)-service', service)
            if res:
                api_name = res.group(1) + '-' + res.group(2)
                if api_name == 'auth-api':
                    endpoint = protocol + '://' + service + "/" + api_name + "/" + res.group(1)
                else:
                    endpoint = protocol + '://' + service + "/" + api_name + "/v1/" + res.group(1) + "s"
                endpoints[api_name] = endpoint
    else:
        if(args.endpoints):
            for endpoint in args.endpoints:
                res = re.search(r'^\/(\w+-\w+)', endpoint)
                if res:
                    endpoints[res.group(1)] = protocol + '://' + base_url + endpoint
        else:
            endpoints = {
            "device-api" : protocol + '://' + base_url + "/device-api/v1/devices",
            "location-api" : protocol + '://' + base_url + "/location-api/v1/locations",
            "ont-api" : protocol + '://' + base_url + "/ont-api/v1/onts",
            "phone-api" : protocol + '://' + base_url + "/phone-api/v1/phones",
            "service-api" : protocol + '://' + base_url + "/service-api/v1/services",
            "subscriber-api" : protocol + '://' + base_url + "/subscriber-api/v1/subscribers",
            "controller-work-api" : protocol + '://' + base_url + "/work-queue-api/v1/controller-work"
            }
        endpoints["auth-api"] = protocol + '://' + base_url + "/auth-api/auth"

    return endpoints

#
# The program
#
endpoints = build_endpoint_dict()

if len(endpoints) > 0 :
    token = get_token(endpoints['auth-api'])

    if(token is None):
        print("No token found, cannot continue")
    else:
        for api in endpoints:
            if api != "auth-api":
                call_rest_endpoint(endpoints[api], token)
else:
    print("No endpoints specified, nothing to do")









