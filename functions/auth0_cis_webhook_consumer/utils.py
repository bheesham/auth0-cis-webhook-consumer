import logging

import requests
from jose import jwt, exceptions
from typing import Optional

from .config import CONFIG

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
    jwks = CONFIG.oidc_discovery_document['jwks']
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


def get_user_profile(user_id: str) -> Optional[dict]:
    """Fetch the user profile from CIS for the user_id

    :param user_id: A CIS user ID
    :return:
    """
    audience = CONFIG.discovery_document['api']['audience']
    token_endpoint = CONFIG.oidc_discovery_document['token_endpoint']
    payload = {
        'client_id': CONFIG.client_id,
        'client_secret': CONFIG.client_secret,
        'audience': audience,
        'grant_type': 'client_credentials'
    }
    response = requests.post(
        url=token_endpoint,
        json=payload
    )
    if response.ok:
        logger.debug('User profile fetched for {} : {}'.format(
            user_id, response.json()))
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
