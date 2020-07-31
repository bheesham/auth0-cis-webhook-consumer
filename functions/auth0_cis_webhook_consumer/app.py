import json
import logging
import traceback
import os

from .config import Config

from .utils import (
    verify_token,
    process_auth0_user
)
from .lambda_types import LambdaDict, LambdaContext

logger = logging.getLogger()
if len(logging.getLogger().handlers) == 0:
    logger.addHandler(logging.StreamHandler())
fmt = "[%(levelname)s] %(asctime)s %(filename)s:%(lineno)d %(message)s\n"
formatter = logging.Formatter(fmt=fmt)
logging.getLogger().handlers[0].setFormatter(formatter)
logging.getLogger('boto3').propagate = False
logging.getLogger('botocore').propagate = False
logging.getLogger('urllib3').propagate = False
logging.getLogger().setLevel(os.getenv('LOG_LEVEL', 'INFO'))
CONFIG = Config()


def process_api_call(
        event: LambdaDict,
        context: LambdaContext,
        cis_webhook_authorization: str,
        body: dict) -> dict:
    """Process an API Gateway call depending on the URL path called

    :param event: The API Gateway request event
    :param context: AWS Lambda context object
    :param cis_webhook_authorization: A bearer token from the CIS webhook
           service
    :param body: The parsed body that was POSTed to the API Gateway
    :return: A dictionary of an API Gateway HTTP response
    """
    if event.get('path') == '/error':
        return {
            'headers': {'Content-Type': 'text/html'},
            'statusCode': 400,
            'body': "Since you requested the /error API endpoint I'll go "
                    "ahead and serve back a 400"}
    elif event.get('path') == '/test':
        return {
            'headers': {'Content-Type': 'text/html'},
            'statusCode': 200,
            'body': 'API request received'}
    elif event.get('path') == '/post':
        if verify_token(
                cis_webhook_authorization,
                CONFIG.notification_jwks,
                CONFIG.notification_oidc_discovery_document['issuer']):
            user_id = body.get('id')
            # https://github.com/mozilla-iam/cis/blob/73f21ab201b4f242512786dfc8e1707fccf7f3c5/python-modules/cis_notifications/cis_notifications/event.py#L44-L51
            operation = body.get('operation')
            if (user_id is not None and operation is not None
                    and process_auth0_user(user_id, operation)):
                return {
                    'headers': {'Content-Type': 'text/html'},
                    'statusCode': 200,
                    'body': 'Update succeeded'}
            else:
                return {
                    'headers': {'Content-Type': 'text/html'},
                    'statusCode': 500,
                    'body': 'Update failed'}
        else:
            return {
                'headers': {'Content-Type': 'text/html'},
                'statusCode': 401,
                'body': "Authorization token invalid"}

    else:
        return {
            'headers': {'Content-Type': 'text/html'},
            'statusCode': 404,
            'body': "That path wasn't found"}


def lambda_handler(event: LambdaDict, context: LambdaContext) -> LambdaDict:
    """Handler for all API Gateway requests

    :param event: AWS API Gateway input fields for AWS Lambda
    :param context: Lambda context about the invocation and environment
    :return: An AWS API Gateway output dictionary for proxy mode
    """
    if event.get('resource') == '/{proxy+}':
        if event.get('httpMethod') != 'POST':
            return {
                'headers': {'Content-Type': 'text/html'},
                'statusCode': 405,
                'body': '405 Method Not Allowed'}
        elif not event.get('body'):
            logger.debug('Missing POST body')
            return {
                'headers': {'Content-Type': 'text/html'},
                'statusCode': 400,
                'body': 'Missing POST body'}
        try:
            headers = (
                {x.lower(): event['headers'][x] for x in event['headers']}
                if event['headers'] is not None else {})
            cis_webhook_authorization = headers.get('authorization')
            body = json.loads(event['body'])
            return process_api_call(event, cis_webhook_authorization, body)
        except json.decoder.JSONDecodeError:
            logger.error('Unable to parse POSTed body : {}'.format(
                event['body']))
        except Exception as e:
            logger.error(str(e))
            logger.error(traceback.format_exc())
            return {
                'headers': {'Content-Type': 'text/html'},
                'statusCode': 500,
                'body': 'Error'}
    else:
        # Not an API Gateway invocation
        return {'error': 'Not an API Gateway invocation'}
