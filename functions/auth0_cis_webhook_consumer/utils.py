import logging

from .config import CONFIG

logger = logging.getLogger(__name__)
logger.setLevel(CONFIG.log_level)


def verify_token(authorization: str, audience: str) -> bool:
    """Verify that bearer token is valid

    :param authorization: Bearer token
    :param audience: Expected audience for the token
    :return:
    """
    return True


def get_user_profile(user_id: str) -> dict:
    """Fetch the user profile from CIS for the user_id

    :param user_id: A CIS user ID
    :return:
    """
    return {'groups': ['ldap_foo', 'mozilliansorg_bar', 'hris_baz']}


def update_auth0_user(user_id: str, profile: dict) -> bool:
    """Update the Auth0 user with the new group list

    :param user_id: The user's user ID
    :param profile: The user's profile
    :return:
    """
    return True