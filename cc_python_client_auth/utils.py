import logging
import os


logger = logging.getLogger(__name__)


class UnconfiguredEnvironment(Exception):
    pass


def get_env_var(name, default=None, raise_exception=False):
    """
    Check to see if an env var is set, return value or raise/log an error if not.

    """

    value = os.environ.get(name, default)

    if value:
        return value

    # Throw/log error if value not provided
    error_msg = "'%s' not set, check env vars."

    if raise_exception:
        raise UnconfiguredEnvironment(error_msg % (name,))

    logger.info(error_msg, name)
