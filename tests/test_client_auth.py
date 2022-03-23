import logging
import os
from unittest.mock import patch

import pytest

from client_auth import get_env_var, requests_client
from client_auth.utils import UnconfiguredEnvironment


ACCESS_TOKEN = (
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6I"
    "kpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyLCJleHAiOjE2NDc5OTY1MDJ9.mxL8544Rx9687CO"
    "4NFG0S0ATOfaZEpzV8Y0QlKZ3_xc"
)


@pytest.fixture(scope="session")
def httpserver_listen_address():
    return ("localhost", 8888)


@pytest.fixture()
def mock_get_client_token(mocker):
    mock_get_new_token_request = mocker.Mock()
    mocker.patch(
        "client_auth.client_requests.requests_with_retry.post",
        mock_get_new_token_request,
    )
    mock_get_new_token_request.return_value = mock_post_response = mocker.Mock()
    mock_post_response.json.return_value = {"access_token": ACCESS_TOKEN}


def test_client_token_aquired_and_appended_to_requests(
    mock_get_client_token, httpserver
):
    endpoint = "/users"
    httpserver.expect_request("/users").respond_with_data({})
    response = requests_client.get(httpserver.url_for(endpoint))

    # The client auth token is aquired and added to
    # the `"Authorization"` header in downstream requests
    assert response.request.headers["Authorization"] == f"Bearer {ACCESS_TOKEN}"


def test_user_id_appended_to_requests(mock_get_client_token, httpserver):
    endpoint = "/users"
    user_id = "12345"
    httpserver.expect_request("/users").respond_with_data({})
    response = requests_client.get(httpserver.url_for(endpoint), user_id=user_id)

    # As a `user_id` kwarg was passed to the request
    # an `ImpersonateAsPrincipal` header was appended
    assert response.request.headers["ImpersonateAsPrincipal"] == user_id


@patch.dict(os.environ, {"TEST_ENV_VAR": "from env"})
def test_get_env_var(mocker):
    # Test get_env_var returns the env var value if set
    value = get_env_var("TEST_ENV_VAR")
    assert value == "from env"

    del os.environ["TEST_ENV_VAR"]

    # expected_error = "'TEST_ENV_VAR' not set, check env vars."
    expected_error = "'%s' not set, check env vars."

    # Test get_env_var raises an error if `raise_exception` flag is set
    with pytest.raises(UnconfiguredEnvironment) as err:
        get_env_var("TEST_ENV_VAR", raise_exception=True)

    assert err.value.args[0] == (expected_error % "TEST_ENV_VAR")

    # Else check error logged out
    logger = logging.getLogger("client_auth.utils")
    mock_error = mocker.Mock()
    mocker.patch.object(logger, "info", mock_error)

    get_env_var("TEST_ENV_VAR")
    mock_error.assert_called_once_with(expected_error, "TEST_ENV_VAR")
