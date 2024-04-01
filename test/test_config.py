import pytest
import os
import boto3
from moto import mock_aws
from functions.auth0_cis_webhook_consumer.config import Config
import logging

logger = logging.getLogger(__name__)

@mock_aws
def test_get_secret_value_success():

    """Test Configuration getting secrets from AWS Secrets Manager"""
    os.environ['AWS_ACCESS_KEY_ID'] = 'fake-access-key'
    os.environ['AWS_SECRET_ACCESS_KEY'] = 'fake-secret-key'
    os.environ['AWS_SECURITY_TOKEN'] = 'fake-security-token'
    os.environ['AWS_SESSION_TOKEN'] = 'fake-session-token'
    os.environ['ENVIRONMENT_NAME'] = 'testing'

    ssm = boto3.client('secretsmanager', region_name='us-west-2')

    """Create the secrets for the tests"""
    ssm.create_secret(
        Name='/iam/cis/testing/auth0_cis_webhook_consumer/personapi_client_secret',
        SecretString='{"/iam/cis/testing/auth0_cis_webhook_consumer/personapi_client_secret":"person-secret-123"}'
    )

    ssm.create_secret(
        Name='/iam/cis/testing/auth0_cis_webhook_consumer/management_api_client_secret',
        SecretString='{"/iam/cis/testing/auth0_cis_webhook_consumer/management_api_client_secret":"mgmt-secret-123"}'
    )


    """
    Most of the work in Config happens in the constructor and
    runs automatically when the object is created. 
    """
    CONFIG = Config()
    assert CONFIG.person_api['client_secret'] == "person-secret-123"
    assert CONFIG.management_api['client_secret'] == "mgmt-secret-123"
