import logging
import os
import json
from typing import Optional

import requests
import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)

def get_secret_value(self, path, secret_name):
    #if the secret exists return it
    print(path, secret_name, self._secrets)
    if secret_name in self._secrets:
        return self._secrets[secret_name]
    else: #otherwise fetch it from AWS Secrets Manager
        try:
            response = boto3.client('secretsmanager').get_secret_value(SecretId=path+secret_name)
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceNotFoundException':
                logger.debug("The requested secret " + secret_name + " was not found")
            elif e.response['Error']['Code'] == 'InvalidRequestException':
                logger.debug("The request was invalid due to: "+ e)
            elif e.response['Error']['Code'] == 'InvalidParameterException':
                logger.debug("The request had invalid params: "+ e)
        else:
            #load the secret as JSON
            secret = json.loads(response['SecretString'])
            #save the secret in the _secrets dictionary
            self._secrets[secret_name] = secret[path+secret_name]
            return secret[path+secret_name]

class Config:
    def __init__(self):
        self._notification_discovery_document = None
        self._notification_oidc_discovery_document = None
        self._notification_jwks = None
        self._secrets = {}
        self._fetched_urls = {}
        self.authorization = {}
        self.domain_name = os.getenv('DOMAIN_NAME')
        self.environment_name = os.getenv('ENVIRONMENT_NAME')
        self.user_whitelist = (
            os.getenv('USER_WHITELIST').split(',')
            if os.getenv('USER_WHITELIST') else None)
        self.notification_discovery_url = os.getenv(
            'NOTIFICATION_DISCOVERY_URL')
        self.notification_audience = os.getenv('NOTIFICATION_AUDIENCE')

        #build path to secrets
        path = '/iam/cis/{}/auth0_cis_webhook_consumer/'.format(
                self.environment_name)

        self.person_api = {
            'client_id': os.getenv('PERSON_API_CLIENT_ID'),
            'client_secret': get_secret_value(self, path, 'personapi_client_secret'),
            'audience': os.getenv('PERSON_API_AUDIENCE'),
            'discovery_url': os.getenv('PERSON_API_DISCOVERY_URL')
        }
        self.management_api = {
            'client_id': os.getenv('MANAGEMENT_API_CLIENT_ID'),
            'client_secret': get_secret_value(self, path,'management_api_client_secret'),
            'audience': os.getenv('MANAGEMENT_API_AUDIENCE'),
            'discovery_url': os.getenv('MANAGEMENT_API_DISCOVERY_URL')
        }

    def get_url(self, url):
        if self._fetched_urls.get(url) is None:
            logger.debug('Fetching URL : {}'.format(url))
            response = requests.get(url)
            if response.ok:
                self._fetched_urls[url] = response.json()
                return self._fetched_urls[url]
            else:
                logger.error('Unable to fetch {} : {} {}'.format(
                    url,
                    response.status_code,
                    response.text
                ))
                return None
        else:
            return self._fetched_urls[url]

    @property
    def notification_discovery_document(self) -> Optional[dict]:
        return self.get_url(self.notification_discovery_url)

    @property
    def notification_oidc_discovery_document(self) -> Optional[dict]:
        return self.get_url(
            self.notification_discovery_document['oidc_discovery_uri'])

    @property
    def notification_jwks(self) -> Optional[dict]:
        return self.get_url(
            self.notification_oidc_discovery_document['jwks_uri'])

    @property
    def personapi_discovery_document(self) -> Optional[dict]:
        return self.get_url(self.person_api['discovery_url'])

    @property
    def management_api_discovery_document(self) -> Optional[dict]:
        return self.get_url(self.management_api['discovery_url'])
