import logging
import os
from base64 import b64encode
from datetime import datetime

import jwt

from client_auth.utils import get_env_var


logger = logging.getLogger(__name__)

TRUTHY_VALUES = ("true", "1")

AUTH_APPEND_CLIENT_TOKEN = (
    os.environ.get("AUTH_APPEND_CLIENT_TOKEN", "false") in TRUTHY_VALUES
)
AUTH_CLIENT_ID = get_env_var("AUTH_CLIENT_ID", raise_exception=AUTH_APPEND_CLIENT_TOKEN)
AUTH_CLIENT_SECRET = get_env_var(
    "AUTH_CLIENT_SECRET", raise_exception=AUTH_APPEND_CLIENT_TOKEN
)
AUTH_TOKEN_ENDPOINT = get_env_var(
    "AUTH_TOKEN_ENDPOINT", raise_exception=AUTH_APPEND_CLIENT_TOKEN
)

CLIENT_TOKEN = None
CLIENT_TOKEN_EXPIRY = None


def get_client_token_expiry_dt(token):
    """
    Decodes a given jwt token and returns a datetime
    representation for the tokens expiry.

    """

    data = jwt.decode(token, options={"verify_signature": False})
    return datetime.fromtimestamp(data["exp"])


def request_new_client_token():
    """
    Acquires a client access grant token from the given `AUTH_TOKEN_ENDPOINT`.

    """

    from client_auth.client_requests import requests_with_retry

    authorization = b64encode(
        bytes(f"{AUTH_CLIENT_ID}:{AUTH_CLIENT_SECRET}", "ISO-8859-1")
    ).decode("ascii")
    headers = {
        "Authorization": f"Basic {authorization}",
        "Content-Type": "application/x-www-form-urlencoded",
    }
    body = {"grant_type": "client_credentials"}
    response = requests_with_retry.post(AUTH_TOKEN_ENDPOINT, headers=headers, data=body)
    response.raise_for_status()
    return response.json()


def process_new_client_token():
    """
    Acquires a client access grant token and sets/returns the
    `CLIENT_TOKEN` and `CLIENT_TOKEN_EXPIRY` global vars.

    """

    result = request_new_client_token()

    # Update and return values
    global CLIENT_TOKEN
    global CLIENT_TOKEN_EXPIRY

    CLIENT_TOKEN = result["access_token"]
    CLIENT_TOKEN_EXPIRY = get_client_token_expiry_dt(CLIENT_TOKEN)

    return (CLIENT_TOKEN, CLIENT_TOKEN_EXPIRY)


def token_has_expired():
    """
    Helper to determine whether an auth token has expired or not.

    """

    if not CLIENT_TOKEN:
        return True

    now = datetime.now()
    return CLIENT_TOKEN_EXPIRY <= now


def get_client_token():
    """
    Returns a cached/new client auth token.

    """

    if not get_client_token:
        return None

    if token_has_expired():
        token, *_ = process_new_client_token()
        return token

    return CLIENT_TOKEN
