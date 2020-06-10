import json
import logging
import traceback

from .config import Config

from .utils import (
    verify_token,
    get_user_profile,
    update_auth0_user
)

CONFIG = Config()
logger = logging.getLogger()
if len(logging.getLogger().handlers) == 0:
    logger.addHandler(logging.StreamHandler())
fmt = "[%(levelname)s] %(asctime)s %(filename)s:%(lineno)d %(message)s\n"
formatter = logging.Formatter(fmt=fmt)
logging.getLogger().handlers[0].setFormatter(formatter)
logging.getLogger().setLevel(CONFIG.log_level)
logging.getLogger('boto3').propagate = False
logging.getLogger('botocore').propagate = False
logging.getLogger('urllib3').propagate = False


def process_api_call(
        event: dict,
        authorization: str,
        body: dict) -> dict:
    """Process an API Gateway call depending on the URL path called

    :param event: The API Gateway request event
    :param authorization: A bearer token
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
        if verify_token(authorization):
            user_id = body.get('id')
            profile = get_user_profile(user_id)
            if (user_id is not None and profile is not None
                    and update_auth0_user(user_id, profile)):
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


def lambda_handler(event: dict, context: dict) -> dict:
    """Handler for all API Gateway requests

    :param event: AWS API Gateway input fields for AWS Lambda
    :param context: Lambda context about the invocation and environment
    :return: An AWS API Gateway output dictionary for proxy mode
    """
    logger.debug('event is {}'.format(event))
    if event.get('resource') == '/{proxy+}':
        try:
            headers = event['headers'] if event['headers'] is not None else {}
            authorization = headers.get('authorization')
            body = json.loads(event['body'])
            return process_api_call(event, authorization, body)
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
