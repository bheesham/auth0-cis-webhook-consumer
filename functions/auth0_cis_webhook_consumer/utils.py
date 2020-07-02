import logging
import time

import requests
import urllib.parse
from jose import jwt, exceptions
from typing import Optional

from .config import Config

logger = logging.getLogger(__name__)
CONFIG = Config()


def filter_profile(item):
    """Strip metadata and signatures from a user profile for easy display"""
    return (
        item if type(item) != dict
        else {key: filter_profile(value) for key, value in item.items()
              if key not in ['metadata', 'signature']})


def verify_token(authorization: str, jwks: dict, issuer: str) -> bool:
    """Verify that bearer token is valid

    :param issuer: Expected issuer of the token
    :param jwks: JSON Web Key Set to verify the token against
    :param authorization: Bearer token
    :return: True if the token is valid otherwise False
    """
    if (len(authorization.split()) != 2
            or authorization.split()[0].lower() != 'bearer'):
        logger.error("Invalid authorization header {}".format(authorization))
        return False

    token = authorization.split()[1]
    try:
        id_token = jwt.decode(
            token=token,
            key=jwks,
            audience=CONFIG.notification_audience,
            issuer=issuer
        )
    except exceptions.JOSEError as e:
        logger.error(
            "Invalid bearer token (issuer : {} audience : {}) : {} : "
            "{}".format(issuer, CONFIG.notification_audience, token, e))
        return False
    logger.debug(
        "Bearer token verified successfully for issuer {} and audience "
        "{}".format(issuer, CONFIG.notification_audience))
    return True


def get_authorization(
        discovery_document: dict,
        client_details: dict) -> Optional[str]:
    """Call a token endpoint to provision an access token and return it

    :param discovery_document: Discovery document containing the token endpoint
    :param client_details: A dictionary containing
               client_id: The OIDC client_id
               client_secret: The associated OIDC client_secret
               audience: The OIDC audience to provision the access token for
    :return: An access token string
    """
    key = '-'.join([discovery_document['issuer'], client_details['audience']])
    if (key in CONFIG.authorization
            and CONFIG.authorization[key]['expiry'] - time.time()) > 300:
        return CONFIG.authorization[key]['token']
    # TODO : Now that we're caching access tokens in AWS Lambda global cache
    # we may want to go further and persist the token into some data store
    # as it's valid for 24 hours
    if client_details.get('client_secret') is None:
        logger.error('Unable to fetch user profile without client_secret')
        return None
    payload = {
        'client_id': client_details['client_id'],
        'client_secret': client_details['client_secret'],
        'audience': client_details['audience'],
        'grant_type': 'client_credentials'
    }
    response = requests.post(
        url=discovery_document['token_endpoint'],
        json=payload
    )
    if not response.ok:
        logger.error(
            'Unable to fetch access token from {} with payload {} : {} '
            '{}'.format(
                discovery_document['token_endpoint'],
                payload, response.status_code, response.text))
        return None
    access_token = response.json().get('access_token')
    token_type = response.json().get('token_type')

    try:
        id_token = jwt.get_unverified_claims(token=access_token)
    except exceptions.JOSEError as e:
        logger.error("Unable to parse token : {} : {}".format(access_token, e))
        return None
    logger.debug('Access token fetched of type {} from {} with audience '
                 '{}'.format(token_type,
                             discovery_document['token_endpoint'],
                             client_details['audience']))
    key = '-'.join([id_token['iss'], id_token['aud']])
    if key not in CONFIG.authorization:
        CONFIG.authorization[key] = {}
    CONFIG.authorization[key]['expiry'] = id_token['exp']
    CONFIG.authorization[key]['token'] = access_token
    return access_token


def get_user_profile(user_id: str) -> Optional[dict]:
    """Fetch the user profile from CIS PersonAPI for the user_id

    :param user_id: A CIS user ID
    :return:
    """
    person_api_authorization = get_authorization(
        CONFIG.personapi_discovery_document,
        CONFIG.person_api)
    if person_api_authorization is None:
        return None
    headers = {'authorization': 'Bearer {}'.format(person_api_authorization)}
    url = 'https://person.{audience}/v2/user/user_id/{escaped_user_id}'.format(
        audience=CONFIG.person_api['audience'],
        escaped_user_id=urllib.parse.quote_plus(user_id)
    )
    response = requests.get(url=url, headers=headers, params={'active': 'Any'})
    if response.ok and response.json().get('uuid', {}).get('value'):
        profile = response.json()
        logger.debug('User profile successfully fetched from {}'.format(
            url))
        return profile
    else:
        logger.error(
            'Unable to fetch valid user profile for {} from {} : {} {}'.format(
                user_id, url, response.status_code, response.text))
        return None


def hack_user_id(user_id):
    """Return a transformed user_id for LDAP users for the dev management API

    If the Auth0 CIS Webhook Consumer is POSTing changes to the auth-dev
    Auth0 management API, then transform any LDAP user_id's from their prod
    syntax to an equivalent dev syntax. This will enable querying the prod
    PersonAPI while writing to the dev Management API

    :param user_id: String of the user's user ID
    :return: Either the original user ID or a transformed user ID
    """
    prod_ldap_user_id_prefix = 'ad|Mozilla-LDAP|'
    dev_ldap_user_id_prefix = 'ad|Mozilla-LDAP-Dev|'
    issuer = CONFIG.management_api_discovery_document['issuer']
    dev_issuer = 'https://auth-dev.mozilla.auth0.com/'
    if user_id.startswith(prod_ldap_user_id_prefix) and issuer == dev_issuer:
        # Hack to translate LDAP user IDs fetched from production and added to
        # Auth0 auth-dev
        result = "{}{}".format(
            dev_ldap_user_id_prefix,
            user_id[len(prod_ldap_user_id_prefix):])
        logger.debug('Hacking user_id from {} to {}'.format(user_id, result))
        return result
    else:
        return user_id


def process_auth0_user(user_id: str, operation: str) -> bool:
    """Process the operation on the Auth0 user

    Requires Auth0 Management API scopes
    * update:users
    * update:users_app_metadata

    :param user_id: The user's user ID
    :param operation: The operation to perform, "create", "update", "delete"
    :return:
    """
    if operation == "create":
        # Would we ever want to trigger user creation in Auth0 because a CIS
        # profile was created? I'd imagine not, as the Auth0 management API
        # create only creates database and passwordless users
        logger.debug(
            "Ignoring request to create {} as we don't do Auth0 user "
            "creation".format(user_id))
        return True

    if CONFIG.management_api_discovery_document is None:
        return False
    auth0_management_api_authorization = get_authorization(
        CONFIG.management_api_discovery_document,
        CONFIG.management_api)
    if auth0_management_api_authorization is None:
        return False
    headers = {'authorization': f'Bearer {auth0_management_api_authorization}'}
    url = '{issuer}api/v2/users/{escaped_user_id}'.format(
        issuer=CONFIG.management_api_discovery_document['issuer'],
        escaped_user_id=urllib.parse.quote_plus(hack_user_id(user_id))
    )

    if operation == "delete":
        # https://github.com/mozilla-iam/auth0-deploy/blob/8659ce4cef35ac22e459b35c09ffcc038b7f9bf8/rules/activate-new-users-in-CIS.js#L36
        payload = {
            'user_metadata': {
                'existsInCIS': False
            }
        }
    elif operation == "update":
        profile = get_user_profile(user_id)
        if profile is None:
            return False
        access_groups = []
        for publisher_name, data in profile.get(
                'access_information', {}).items():
            if data.get('values') is None:
                continue
            for value in data['values']:
                if publisher_name == 'ldap':
                    access_groups.append(value)
                elif publisher_name == 'hris':
                    # The hris section of access_information doesn't contain
                    # groups, but instead contains employee_id, worker_type etc
                    continue
                elif publisher_name == 'access_provider':
                    # The access_provider section of access_information doesn't
                    # seem to contain groups (or anything)
                    continue
                else:
                    # prepend "publisher_" to all groups except those from
                    # the ldap publisher
                    access_groups.append('_'.join([publisher_name, value]))

        payload = {
            'app_metadata': {
                'groups': access_groups
            }
        }
    else:
        logger.error('Unknown operation {}'.format(operation))
        return False

    if CONFIG.user_whitelist is not None:
        if user_id in CONFIG.user_whitelist:
            logger.info(
                'Performing Auth0 update on {} as the user is in the '
                'whitelist'.format(user_id))
        else:
            logger.debug(
                'Skipping Auth0 update on {} as the user is not in the '
                'whitelist'.format(user_id))
            return True
    # https://auth0.com/docs/api/management/v2/#!/Users/patch_users_by_id
    response = requests.patch(
        url=url,
        json=payload,
        headers=headers)
    if not response.ok:
        logger.error(
            'Auth0 Management API profile update failed {} : {} : {}'.format(
                url,
                payload,
                response.text))
    else:
        logger.info('Successfully updated Auth0 user {} : {}'.format(
            user_id, payload))
    return response.ok
