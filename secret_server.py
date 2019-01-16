import os
import configparser
import sys
import requests
from requests_ntlm import HttpNtlmAuth

config = configparser.ConfigParser()
config.read("secret_server.cfg")


secret_server_uri = config['secret_server_rest_api']['http_address']

username = config['secret_server_credentials']['username']
password = config['secret_server_credentials']['password']


def generate_random_password():
    try:
        api = secret_server_uri + "secret-templates/generate-password/7"
        secret_password = requests.post(
            api, auth=HttpNtlmAuth(username, password))
        return secret_password.json()
    except:
        error = sys.exc_info()
        print(error)


def retrieve_secret_id(secret_name):
    try:
        secrets = requests.get(secret_server_uri+"secrets?filter.searchText="+secret_name+"",
                               auth=HttpNtlmAuth(username, password))
        json_request = secrets.json()
        secret_name_found = json_request['records'][0]['name']
        if(secret_name_found.lower() == secret_name.lower()):

            secret_id = json_request['records'][0]['id']
            return secret_id
        else:
            return "Secrets are not the same. Type the exact secret name"
    except:
        error = sys.exc_info()
        print(error)


def retrieve_group_id(group_name):
    try:
        groups = requests.get(secret_server_uri+"groups?filter.searchText="+group_name+"",
                               auth=HttpNtlmAuth(username, password))
        json_request = groups.json()
        group_name_found = json_request['records'][0]['name']
        if(group_name_found.lower() == group_name.lower()):

            secret_id = json_request['records'][0]['id']
            return secret_id
        else:
            return "Groups are not the same. Type the exact group name"
    except:
        error = sys.exc_info()
        print(error)


def retrieve_secret_password(secret_name):
    try:
        secret_id = retrieve_secret_id(secret_name)
        secret = requests.get(secret_server_uri+"secrets/"+str(secret_id)+"",
                              auth=HttpNtlmAuth(username, password))
        json_request = secret.json()
        json_request = json_request['items']
        for att in json_request:
            if(att['slug'] == "password"):
                return att['itemValue']
    except:
        error = sys.exc_info()
        print(error)


def retrieve_folder_properties(FolderName):
    try:
        folder_properties = requests.get(
            secret_server_uri+"folders?filter.searchText="+FolderName+"", auth=HttpNtlmAuth(username, password))
        json_request = folder_properties.json()
        folder_id = json_request['records'][0]['id']
        return folder_id
    except:
        error = sys.exc_info()
        print(error)


def add_new_secret(FolderName, secret_name, notes):
    try:
        secret_password = generate_random_password()
        folder_id = retrieve_folder_properties(FolderName)

        # SecretTypeID = 2 it is used for the password type
        secret_type_id = 2
        secret_template = requests.get(secret_server_uri+"secrets/stub?filter.secretTemplateId="+str(
            secret_type_id)+"", auth=HttpNtlmAuth(username, password))

        json_request = secret_template.json()

        json_request['name'] = secret_name
        json_request['SiteId'] = 1
        json_request['secretTemplateId'] = secret_type_id
        json_request['folderId'] = folder_id

        json_request['items'][0]['itemValue'] = secret_name
        json_request['items'][1]['itemValue'] = secret_name
        json_request['items'][2]['itemValue'] = secret_password
        json_request['items'][3]['itemValue'] = notes

        new_secret = requests.post(
            secret_server_uri+"secrets/", json=json_request, auth=HttpNtlmAuth(username, password))
        print(new_secret.content)
    except:
        error = sys.exc_info()
        print(error)


def share_secret_to_group(secret_name, group_name, secret_permission):
    try:
        possible_permissions = ["Owner", "Edit", "View", "List"]

        if any(secret_permission in s for s in possible_permissions):
            pass
        else:
            return "There is no permission named: " + secret_permission


        secret_id = retrieve_secret_id(secret_name)
        group_id = retrieve_group_id(group_name)

        secret_permissions = requests.get(
                    secret_server_uri+"secret-permissions?filter.secretId="+str(secret_id)+"", auth=HttpNtlmAuth(username, password))
        json_request = secret_permissions.json()

        json_request['secretId'] = secret_id
        json_request['groupId'] = group_id
        json_request['secretAccessRoleName'] = secret_permission
        json_request['KnownAs'] = group_name

        secret_permissions = requests.post(
                    secret_server_uri+"secret-permissions", json=json_request, auth=HttpNtlmAuth(username, password))

        return secret_permissions.content


    except:
        error = sys.exc_info()
        print(error)


def run_active_directory_synchronization():
    try:
        ad_sync = requests.post(secret_server_uri+"active-directory/synchronize",auth=HttpNtlmAuth(username,password))
        return ad_sync.json()
    except:
        error = sys.exc_info()
        print(error)
