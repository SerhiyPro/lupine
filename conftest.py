import pytest

from lupine import API


@pytest.fixture
def api():
    return API()


@pytest.fixture
def client(api):
    return api.test_session()
