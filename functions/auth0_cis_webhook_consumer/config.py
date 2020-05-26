import logging
import os

import requests
import boto3

logger = logging.getLogger()


def get_paginated_results(product, action, key, credentials=None, args=None):
    args = {} if args is None else args
    credentials = {} if credentials is None else credentials
    return [y for sublist in [x[key] for x in boto3.client(
        product, **credentials).get_paginator(action).paginate(**args)]
            for y in sublist]


class Config:
    def __init__(self):
        self.log_level = os.getenv('LOG_LEVEL', 'INFO')
        self.domain_name = os.getenv('DOMAIN_NAME')
        self.environment_name = os.getenv('ENVIRONMENT_NAME')
        self.discovery_url = os.getenv(
            'DISCOVERY_URL',
            'https://auth.mozilla.com/.well-known/mozilla-iam')
        self.notification_audience = os.getenv('NOTIFICATION_AUDIENCE')
        self.client_id = os.getenv('CLIENT_ID')
        logging.getLogger().setLevel(self.log_level)
        self.discovery_document = None
        self.oidc_discovery_document = None
        self.get_discovery_document()
        self.client_secret = None
        self.get_parameter_store_values()

    def get_discovery_document(self) -> None:
        """Fetch the IAM discovery document and enrich it with the OIDC
        discovery document and the JWKS.
        If the discovery_document is not available in AWS Lambda cache, fetch
        the CONFIG.discovery_url and parse it into a dictionary. Fetch the
        content of the oidc_discovery_uri and the jwks_uri and add it to the
        dictionary
        :return:
        """
        logger.debug('Fetching discovery documents')
        self.discovery_document = requests.get(self.discovery_url).json()
        # TODO : This won't work in dev due to this bug https://github.com/mozilla-iam/cis/issues/239#issuecomment-633789313
        self.oidc_discovery_document = requests.get(
            self.discovery_document['oidc_discovery_uri']).json()
        self.oidc_discovery_document['jwks'] = requests.get(
            self.oidc_discovery_document['jwks_uri']).json()

    def get_parameter_store_values(self) -> None:
        """Fetch secrets from AWS SSM Parameter Store

        :return:
        """
        path = '/iam/cis/{}/auth0_cis_webhook_consumer/'.format(
            self.environment_name)
        args = {
            'Path': path[:-1],
            'WithDecryption': True
        }
        parameters = get_paginated_results(
            'ssm', 'get_parameters_by_path', 'Parameters', args=args)
        logger.debug('Fetched {} parameters from AWS SSM'.format(
            len(parameters)))
        for parameter in parameters:
            name = parameter['Name']
            setattr(
                self,
                name[name.startswith(path) and len(path):],
                parameter['Value']
            )


# TODO : Confirm that CONFIG is a global from AWS Lambda's perspective and that
# it gets cached and doesn't refetch discovery docs and paramters when it's
# imported in each module
CONFIG = Config()
