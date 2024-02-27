import pytest
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from services.config_loader import Config

# Path to your test configuration file
TEST_CONFIG_PATH = "tests/config/test_config.ini"

@pytest.fixture
def test_config():
    return Config(config_file=TEST_CONFIG_PATH)

def test_oauth_config_loading(test_config):
    assert test_config.oauth.client_id == "test-client-id"
    assert test_config.oauth.client_secret == "test-secret-key"
    assert test_config.oauth.authorization_url == "https://oauth.testsite.com/OAuth/Authorize"
    assert test_config.oauth.token_url == "https://oauth.testsite.com/OAuth/Token"
    assert test_config.oauth.scopes == "test:scopes"

def test_server_config_loading(test_config):
    assert test_config.server.local_port == 9090
    assert test_config.server.get_local_url() == "http://localhost:9090"
    assert test_config.server.get_redirect_uri() == "http://localhost:9090/callback"

def test_public_api_config_loading(test_config):
    assert test_config.public_api.list_athletes_endpoint == "https://api.testsite.com/v1/test/athletes"
