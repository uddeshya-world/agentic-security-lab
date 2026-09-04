import os

import pytest

# These tests run from two places: the host, where the stack is published on
# localhost, and inside the agent container, where the tools answer to their
# compose service names. Prefer an explicit *_HOST override, then the in-network
# URL the app itself is configured with, then localhost — so the same suite is
# green either way instead of failing with connection errors in one of them.
AGENT_URL = os.environ.get("AGENT_URL", "http://localhost:8000")
MAILHOG_API = os.environ.get("MAILHOG_API_BASE", "http://localhost:8025")
DB_TOOL_URL = os.environ.get("DB_TOOL_URL_HOST") or os.environ.get("DB_TOOL_URL", "http://localhost:8101")
EMAIL_TOOL_URL = os.environ.get("EMAIL_TOOL_URL_HOST") or os.environ.get("EMAIL_TOOL_URL", "http://localhost:8102")
FILE_TOOL_URL = os.environ.get("FILE_TOOL_URL_HOST") or os.environ.get("FILE_TOOL_URL", "http://localhost:8103")


@pytest.fixture(scope="session")
def agent_url():
    return AGENT_URL


@pytest.fixture(scope="session")
def mailhog_api():
    return MAILHOG_API


@pytest.fixture(scope="session")
def db_tool_url():
    return DB_TOOL_URL


@pytest.fixture(scope="session")
def email_tool_url():
    return EMAIL_TOOL_URL


@pytest.fixture(scope="session")
def file_tool_url():
    return FILE_TOOL_URL
