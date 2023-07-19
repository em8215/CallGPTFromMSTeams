import os
import requests
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)

# 
def get_parameter(parameter_name:str) -> str:
    '''Get a parameter from AWS Parameter Store with Lambda extention'''
    endpoint = 'http://localhost:2773/systemsmanager/parameters/get/?name={}'.format(parameter_name)
    headers = {
        'X-Aws-Parameters-Secrets-Token': os.environ['AWS_SESSION_TOKEN']
    }
    res = requests.get(endpoint, headers=headers)

    return res.json()['Parameter']['Value']


def get_encrypted_parameter(parameter_name:str) -> str:
    ''' Get a encrypted parameter from AWS Parameter Store with Lambda extention'''
    endpoint = 'http://localhost:2773/systemsmanager/parameters/get/?withDecryption=true&name={}'.format(parameter_name)
    headers = {
        'X-Aws-Parameters-Secrets-Token': os.environ['AWS_SESSION_TOKEN']
    }
    res = requests.get(endpoint, headers=headers)

    return res.json()['Parameter']['Value']