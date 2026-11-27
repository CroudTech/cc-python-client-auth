import pytest


@pytest.fixture
def access_token():
    return (  # nosec
        "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6I"
        "kpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyLCJleHAiOjE2NDc5OTY1MDJ9.mxL8544Rx9687CO"
        "4NFG0S0ATOfaZEpzV8Y0QlKZ3_xc"
    )


@pytest.fixture(scope="session")
def httpserver_listen_address():
    return ("localhost", 8888)


@pytest.fixture()
def mock_get_client_token(mocker, access_token):
    mock_get_new_token_request = mocker.Mock()
    mocker.patch(
        "cc_python_client_auth.client_requests.requests_with_retry.post",
        mock_get_new_token_request,
    )
    mock_get_new_token_request.return_value = mock_post_response = mocker.Mock()
    mock_post_response.json.return_value = {"access_token": access_token}
