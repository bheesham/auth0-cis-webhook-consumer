import logging
import os
from typing import Optional

import requests
import boto3

logger = logging.getLogger(__name__)


def get_paginated_results(product, action, key, credentials=None, args=None):
    args = {} if args is None else args
    credentials = {} if credentials is None else credentials
    return [y for sublist in [x[key] for x in boto3.client(
        product, **credentials).get_paginator(action).paginate(**args)]
            for y in sublist]


class Config:
    def __init__(self):
        self._notification_discovery_document = None
        self._notification_oidc_discovery_document = None
        self._notification_jwks = None
        self._secrets = None
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
        self.person_api = {
            'client_id': os.getenv('PERSON_API_CLIENT_ID'),
            'client_secret': self.secrets.get('personapi_client_secret'),
            'audience': os.getenv('PERSON_API_AUDIENCE'),
            'discovery_url': os.getenv('PERSON_API_DISCOVERY_URL')
        }
        self.management_api = {
            'client_id': os.getenv('MANAGEMENT_API_CLIENT_ID'),
            'client_secret': self.secrets.get(
                'management_api_client_secret'),
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

    @property
    def secrets(self) -> dict:
        if self._secrets is None:
            path = '/iam/cis/{}/auth0_cis_webhook_consumer/'.format(
                self.environment_name)
            args = {'Path': path[:-1], 'WithDecryption': True}
            parameters = get_paginated_results(
                'ssm', 'get_parameters_by_path', 'Parameters', args=args)
            logger.debug('Fetched {} parameters from AWS SSM'.format(
                len(parameters)))
            self._secrets = {}
            for parameter in parameters:
                name = parameter['Name'][len(path):]
                self._secrets[name] = parameter['Value']
        return self._secrets
