import logging
import os
from typing import Optional

import requests
import boto3


def get_paginated_results(product, action, key, credentials=None, args=None):
    args = {} if args is None else args
    credentials = {} if credentials is None else credentials
    return [y for sublist in [x[key] for x in boto3.client(
        product, **credentials).get_paginator(action).paginate(**args)]
            for y in sublist]


class Config:
    def __init__(self):
        self.log_level = os.getenv('LOG_LEVEL', 'INFO')
        self.logger = logging.getLogger()
        self.logger.setLevel(self.log_level)
        self.domain_name = os.getenv('DOMAIN_NAME')
        self.environment_name = os.getenv('ENVIRONMENT_NAME')
        self.discovery_url = os.getenv(
            'DISCOVERY_URL',
            'https://auth.mozilla.com/.well-known/mozilla-iam')
        self.notification_audience = os.getenv('NOTIFICATION_AUDIENCE')
        self.client_id = os.getenv('CLIENT_ID')
        self._discovery_document = None
        self._oidc_discovery_document = None
        self._jwks = None
        self._secrets = None

    def get_url(self, url):
        response = requests.get(url)
        if response.ok:
            return response.json()
        else:
            self.logger.error('Unable to fetch {} : {} {}'.format(
                url,
                response.status_code,
                response.text
            ))
            return None

    @property
    def discovery_document(self) -> dict:
        if self._discovery_document is None:
            self.logger.debug('Fetching discovery document')
            self._discovery_document = self.get_url(self.discovery_url)
        return self._discovery_document

    @property
    def oidc_discovery_document(self) -> Optional[dict]:
        if self._oidc_discovery_document is None:
            if self.discovery_document is None:
                self.logger.error(
                    'Unable to fetch OIDC discovery document : URL unknown')
                return None
            self.logger.debug('Fetching OIDC discovery document')
            self._oidc_discovery_document = self.get_url(
                self.discovery_document['oidc_discovery_uri'])
        return self._oidc_discovery_document

    @property
    def jwks(self) -> Optional[dict]:
        if self._jwks is None:
            if self.oidc_discovery_document is None:
                self.logger.error('Unable to fetch JWKS : URL unknown')
                return None
            self.logger.debug('Fetching JWKS')
            self._jwks = self.get_url(
                self.oidc_discovery_document['jwks_uri'])
        return self._jwks

    @property
    def secrets(self) -> dict:
        if self._secrets is None:
            path = '/iam/cis/{}/auth0_cis_webhook_consumer/'.format(
                self.environment_name)
            args = {'Path': path[:-1], 'WithDecryption': True}
            parameters = get_paginated_results(
                'ssm', 'get_parameters_by_path', 'Parameters', args=args)
            self.logger.debug('Fetched {} parameters from AWS SSM'.format(
                len(parameters)))
            self._secrets = {}
            for parameter in parameters:
                name = parameter['Name'][len(path):]
                self._secrets[name] = parameter['Value']
        return self._secrets
