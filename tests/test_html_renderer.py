import pytest
from unittest.mock import patch, MagicMock
import time
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from services.html_renderer import HtmlRenderer
from services.application_state import ApplicationState
from services.config_loader import Config

@pytest.fixture
def mock_config():
    return Config("tests/config/test_config.ini")

@pytest.fixture
def mock_state():
    state = ApplicationState()
    state.authorization_code_response = MagicMock(authorization_code=None)
    state.token_code_response = MagicMock(access_token=None, refresh_token=None, access_token_expire=0)
    state.list_athletes_response = MagicMock(data=None)
    return state

@pytest.fixture
def html_renderer(mock_config, mock_state):
    return HtmlRenderer(config=mock_config, state=mock_state)

def test_get_auth_link(html_renderer):
    expected_url = ('<a href="https://example.com/auth?response_type=code'
                    '&client_id=client_id_example&redirect_uri=https://localhost/redirect'
                    '&scope=read,write">Authorize</a>')
    assert html_renderer.get_auth_link("https://example.com/auth", "client_id_example", 
                                       "https://localhost/redirect", "read,write") == expected_url

def test_get_authorization_value_with_no_code(html_renderer):
    assert 'Authorize' in html_renderer.get_authorization_value()

def test_get_authorization_value_with_code(html_renderer, mock_state):
    mock_state.is_authorization_complete = MagicMock(return_value=True)
    mock_state.authorization_code_response.authorization_code = "auth_code_example"
    assert html_renderer.get_authorization_value() == "auth_code_example"

def test_get_token_value_with_no_authorization(html_renderer):
    assert html_renderer.get_token_value() == ""

def test_get_token_value_with_authorization_no_token(html_renderer, mock_state):
    mock_state.is_authorization_complete = MagicMock(return_value=True)
    assert 'Get Token' in html_renderer.get_token_value()

def test_get_token_value_with_expired_token(html_renderer, mock_state):
    mock_state.is_authorization_complete = MagicMock(return_value=True)
    mock_state.is_token_complete = MagicMock(return_value=True)
    mock_state.token_code_response.is_token_expired = MagicMock(return_value=True)
    assert 'Refresh Token' in html_renderer.get_token_value()

def test_get_token_value_with_valid_token(html_renderer, mock_state):
    mock_state.is_authorization_complete = MagicMock(return_value=True)
    mock_state.is_token_complete = MagicMock(return_value=True)
    mock_state.token_code_response.is_token_expired = MagicMock(return_value=False)
    mock_state.token_code_response.access_token = "access_token_example"
    mock_state.token_code_response.refresh_token = "refresh_token_example"
    mock_state.token_code_response.access_token_expire = time.time() + 3600  # 1 hour from now
    assert '"Token": "access_token_example"' in html_renderer.get_token_value()

def test_get_list_athletes_value_no_authorization(html_renderer):
    assert html_renderer.get_list_athletes_value() == ""

def test_get_list_athletes_value_with_authorization_no_token(html_renderer, mock_state):
    mock_state.is_authorization_complete = MagicMock(return_value=True)
    assert html_renderer.get_list_athletes_value() == ""

def test_get_list_athletes_value_with_expired_token(html_renderer, mock_state):
    mock_state.is_authorization_complete = MagicMock(return_value=True)
    mock_state.is_token_complete = MagicMock(return_value=True)
    mock_state.token_code_response.is_token_expired = MagicMock(return_value=True)
    assert html_renderer.get_list_athletes_value() == "Token Expired, Refresh Token."

def test_get_list_athletes_value_with_valid_token_no_data(html_renderer, mock_state):
    mock_state.is_authorization_complete = MagicMock(return_value=True)
    mock_state.is_token_complete = MagicMock(return_value=True)
    mock_state.token_code_response.is_token_expired = MagicMock(return_value=False)
    assert 'Make Example Call' in html_renderer.get_list_athletes_value()

def test_get_list_athletes_value_with_data(html_renderer, mock_state):
    mock_state.is_authorization_complete = MagicMock(return_value=True)
    mock_state.is_token_complete = MagicMock(return_value=True)
    mock_state.token_code_response.is_token_expired = MagicMock(return_value=False)
    mock_state.is_list_athletes_complete = MagicMock(return_value=True)
    mock_state.list_athletes_response.data = "Athlete data example"
    assert 'Athlete data example' in html_renderer.get_list_athletes_value()

def test_render_with_exception(html_renderer, mock_state):
    mock_state.exception_text = "Test exception"
    assert "Test exception" in html_renderer.render()
    assert 'Authorization Code Request' in html_renderer.render()

def test_render_initial_state(html_renderer):
    rendered_html = html_renderer.render()
    assert "Authorize" in rendered_html
    assert "Authorization Code Request" in rendered_html

def test_render_after_authorization(html_renderer, mock_state):
    mock_state.is_authorization_complete = MagicMock(return_value=True)
    rendered_html = html_renderer.render()
    assert "Get Token" in rendered_html
    assert "Token Request" in rendered_html

def test_render_after_token_acquisition(html_renderer, mock_state):
    mock_state.is_authorization_complete = MagicMock(return_value=True)
    mock_state.is_token_complete = MagicMock(return_value=True)
    mock_state.token_code_response.is_token_expired = MagicMock(return_value=False)
    rendered_html = html_renderer.render()
    assert "Make Example Call" in rendered_html
    assert "get-test-data" in rendered_html
