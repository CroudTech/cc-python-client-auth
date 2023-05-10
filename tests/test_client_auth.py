import logging
import os
from unittest.mock import patch

import pytest

from cc_python_client_auth import get_env_var, requests_client
from cc_python_client_auth.utils import UnconfiguredEnvironment


@pytest.mark.parametrize("append_auth", ["true", "false"])
def test_client_token_aquired_and_appended_to_requests(
    append_auth, mock_get_client_token, httpserver, access_token
):
    os.environ["AUTH_APPEND_CLIENT_TOKEN"] = append_auth
    endpoint = "/users"
    httpserver.expect_request("/users").respond_with_data({})
    response = requests_client.get(httpserver.url_for(endpoint))  # nosec

    if append_auth == "true":
        # The client auth token is aquired and added to
        # the `"Authorization"` header in downstream requests
        assert response.request.headers["Authorization"] == f"Bearer {access_token}"
    else:
        assert "Authorization" not in response.request.headers


def test_user_id_appended_to_requests(mock_get_client_token, httpserver):
    endpoint = "/users"
    user_id = "12345"
    httpserver.expect_request("/users").respond_with_data({})
    response = requests_client.get(
        httpserver.url_for(endpoint), user_id=user_id
    )  # nosec

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
    logger = logging.getLogger("cc_python_client_auth.utils")
    mock_error = mocker.Mock()
    mocker.patch.object(logger, "info", mock_error)

    get_env_var("TEST_ENV_VAR")
    mock_error.assert_called_once_with(expected_error, "TEST_ENV_VAR")
