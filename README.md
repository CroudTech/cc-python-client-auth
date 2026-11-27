# cc-python-client-auth

This package provides a custom requests client `client_requests`.

When utilised it will automatically aquire and append a client auth grant token to any downstream requests for use when making internal service to service requests.

It also provides other helpers to simply aquire a client auth token if needed.

## Environment Variables:

| Name                     | Description                                                                                     |
| ------------------------ | ----------------------------------------------------------------------------------------------- |
| AUTH_APPEND_CLIENT_TOKEN | Whether or not to acquire and append an auth token header to requests made with requests_client |
| AUTH_CLIENT_ID           | The client credentials client ID. Required for the token exchange                               |
| AUTH_CLIENT_SECRET       | The client credentials secret. Also required for the token exchange                             |
| AUTH_TOKEN_ENDPOINT      | The aquire token endpoint                                                                       |
| DEFAULT_REQUEST_TIMEOUT  | Timeout value (seconds) for requests made with requests_client (Default: 10)                    |

## Usage:

### Making Requests:

The syntax is exactly the same as making a request directly with the `requests` package

```python
from cc_python_client_auth import requests_client

response = requests_client.get("example.com/users")
response.response.raise_for_status()
return response.json()
```

### Optional Request Params:

**user_id:**

Optionally you can also added a `user_id` param to the request syntax where user impersonation is required, this will append the `user_id` value as a `ImpersonateAsPrincipal` header to be processed in the target service

```python
from cc_python_client_auth import requests_client

response = requests_client.get("example.com/users", user_id="12345")
response.response.raise_for_status()
return response.json()
```

**Result:**

An additional `ImpersonateAsPrincipal` header is added to the request

e.g `{"ImpersonateAsPrincipal": "12345"}`

### Timeouts:

A default timeout value of `10` is set on requests you can override this by setting a value in the optional `DEFAULT_REQUEST_TIMEOUT` ENV VAR or per request by adding `timeout={value}` to a request

### Retries:

For convenience add an exponential retry config is also added to the request client, requests will be retried three times

### Additional helpers:

**request_new_client_token:**

If you would prefer to simply retrieve a get client token response you can call this method directly

```python
from cc_python_client_auth import request_new_client_token

get_token_response = request_new_client_token()
```

**requests_with_retry:**

This is another requests client without the auth applied but will retry on failures as above

```python
from cc_python_client_auth import requests_with_retry

response = requests_with_retry.get("example.com/users")
response.response.raise_for_status()
return response.json()
```

**get_env_var:**

A helper method for getting env vars and optionally raising an exception if no values are provided

```python
from cc_python_client_auth import get_env_var

my_var = get_env_var("MY_VAR", default="My Value", raise_exception=True)
```
