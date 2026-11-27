import logging
import os

import requests
from requests.adapters import HTTPAdapter
from requests.auth import AuthBase
from requests.packages.urllib3.util.retry import Retry

from . import client_auth


REQUEST_TIMEOUT = os.environ.get("DEFAULT_REQUEST_TIMEOUT", 10)

logger = logging.getLogger(__name__)


class CustomSession(requests.Session):
    """
    Additionally allows a `user_id` kwarg to be passed to requests
    which is added as the value of an `ImpersonateAsPrincipal` header.

    """

    def request(self, method, url, **kwargs):
        if "user_id" in kwargs:
            user_id = kwargs["user_id"]
            del kwargs["user_id"]
            self.headers["ImpersonateAsPrincipal"] = user_id

        return super().request(method, url, **kwargs)


class TimeoutHTTPAdapter(HTTPAdapter):
    def __init__(self, *args, **kwargs):
        self.timeout = REQUEST_TIMEOUT
        if "timeout" in kwargs:
            self.timeout = kwargs["timeout"]
            del kwargs["timeout"]
        super().__init__(*args, **kwargs)

    def send(self, request, **kwargs):
        timeout = kwargs.get("timeout")
        if timeout is None:
            kwargs["timeout"] = self.timeout

        try:
            result = super().send(request, **kwargs)
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                # Clear the cached token so a new one will
                # be aquired on the next request
                client_auth.CLIENT_TOKEN = None

            raise

        except Exception:
            logger.exception("Error:")
        else:
            return result


class ClientAuth(AuthBase):
    """
    Attaches client authentication to the given Request object.

    """

    def __call__(self, request):
        # modify and return the request
        if bearer_token := client_auth.get_client_token():
            request.headers["Authorization"] = f"Bearer {bearer_token}"

        return request


retry_strategy = Retry(
    total=3,
    backoff_factor=1,
    status_forcelist=[401, 429, 500, 502, 503, 504],
    allowed_methods=[
        "HEAD",
        "GET",
        "PUT",
        "POST",
        "PATCH",
        "DELETE",
        "OPTIONS",
        "TRACE",
    ],
)
adapter = TimeoutHTTPAdapter(max_retries=retry_strategy)

requests_with_retry = CustomSession()
requests_with_retry.mount("https://", adapter)
requests_with_retry.mount("http://", adapter)

requests_client = CustomSession()
requests_client.auth = ClientAuth()
requests_client.mount("https://", adapter)
requests_client.mount("http://", adapter)
