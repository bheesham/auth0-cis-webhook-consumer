import logging

import requests
import urllib.parse
from jose import jwt, exceptions
from typing import Optional


from .config import Config

CONFIG = Config()
logger = logging.getLogger(__name__)
logger.setLevel(CONFIG.log_level)


def verify_token(authorization: str) -> bool:
    """Verify that bearer token is valid

    :param authorization: Bearer token
    :return: True if the token is valid otherwise False
    """
    if (len(authorization.split()) != 2
            or authorization.split()[0].lower() != 'bearer'):
        logger.error("Invalid authorization header {}".format(authorization))
        return False

    token = authorization.split()[1]
    jwks = CONFIG.jwks
    issuer = CONFIG.oidc_discovery_document['issuer']

    try:
        id_token = jwt.decode(
            token=token,
            key=jwks,
            audience=CONFIG.notification_audience,
            issuer=issuer
        )
    except exceptions.JOSEError as e:
        logger.error("Invalid bearer token : {}".format(e))
        return False
    logger.debug("Valid bearer token : {}".format(id_token))
    return True


def get_authorization() -> Optional[str]:
    if CONFIG.secrets.get('client_secret') is None:
        logger.error('Unable to fetch user profile without client_secret')
        return None
    audience = CONFIG.discovery_document['api']['audience']
    token_endpoint = CONFIG.oidc_discovery_document['token_endpoint']
    payload = {
        'client_id': CONFIG.client_id,
        'client_secret': CONFIG.secrets['client_secret'],
        'audience': audience,
        'grant_type': 'client_credentials'
    }
    # TODO : We could get the access token in app.py maybe and save it as a global
    # so it's available for future instantiations without reprovisioning a token
    # or maybe we persist it somewhere based on it's "expires_in" value
    response = requests.post(
        url=token_endpoint,
        json=payload
    )
    if not response.ok:
        logger.error('Unable to fetch access token : {} {}'.format(
            response.status_code, response.text))
        return None
    access_token = response.json().get('access_token')
    token_type = response.json().get('token_type')
    logger.debug('Access token fetched of type {}'.format(token_type))
    return "{} {}".format(token_type, access_token)


def get_user_profile(user_id: str) -> Optional[dict]:
    """Fetch the user profile from CIS for the user_id

    :param user_id: A CIS user ID
    :return:
    """
    headers = {'authorization': get_authorization()}
    url = "/".join([
        CONFIG.discovery_document['api']['endpoints']['person'],
        'v2/user/user_id',
        urllib.parse.quote_plus(user_id)
    ])
    logger.debug('Querying URL {} with headers {}'.format(url, headers))
    response = requests.get(url=url, headers=headers)
    if response.ok:
        logger.debug('User profile fetched for {} : {}'.format(user_id, response.json().get('access_information')))
        return response.json()
    else:
        logger.error('Unable to fetch user profile for {} : {} {}'.format(
            user_id, response.status_code, response.text))
        return None


def update_auth0_user(user_id: str, profile: dict) -> bool:
    """Update the Auth0 user with the new group list

    :param user_id: The user's user ID
    :param profile: The user's profile
    :return:
    """
    return True
