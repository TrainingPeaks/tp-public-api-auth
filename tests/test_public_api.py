import json
import pytest
from unittest.mock import patch, MagicMock
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from services.public_api import GetTokenRequest, ListAthleteRequest, RefreshTokenRequest

# Sample data for testing
AUTHORIZATION_CODE = "test_code"
CLIENT_ID = "client_id"
CLIENT_SECRET = "client_secret"
REDIRECT_URI = "http://localhost/callback"
TOKEN_URL = "https://oauth.example.com/token"
LIST_ATHLETES_URL = "https://api.example.com/athletes"
ACCESS_TOKEN = "access_token"
REFRESH_TOKEN = "refresh_token"


@pytest.fixture
def token_response_mock():
    """Mock response for the token request"""
    return {
        "access_token": ACCESS_TOKEN,
        "token_type": "Bearer",
        "expires_in": 3600,
        "refresh_token": REFRESH_TOKEN,
        "scope": "read write",
    }


@pytest.fixture
def athlete_list_response_mock():
    """Mock response for the list athlete request"""
    return [
        {"id": 1, "name": "Athlete One"},
        {"id": 2, "name": "Athlete Two"},
    ]


@patch("requests.post")
def test_get_token_request(mock_post, token_response_mock):
    mock_post.return_value = MagicMock(
        status_code=200, json=lambda: token_response_mock
    )

    response = GetTokenRequest(AUTHORIZATION_CODE, REDIRECT_URI).execute(
        TOKEN_URL, CLIENT_ID, CLIENT_SECRET
    )

    assert response.access_token == ACCESS_TOKEN
    assert response.refresh_token == REFRESH_TOKEN
    mock_post.assert_called_once()


@patch("requests.post")
def test_refresh_token_request(mock_post, token_response_mock):
    mock_post.return_value = MagicMock(
        status_code=200, json=lambda: token_response_mock
    )

    response = RefreshTokenRequest(REFRESH_TOKEN).execute(
        TOKEN_URL, CLIENT_ID, CLIENT_SECRET
    )

    assert response.access_token == ACCESS_TOKEN
    assert response.refresh_token == REFRESH_TOKEN
    mock_post.assert_called_once()


@patch("requests.get")
def test_list_athlete_request(mock_get, athlete_list_response_mock):
    mock_get.return_value = MagicMock(
        status_code=200, json=lambda: athlete_list_response_mock
    )

    response = ListAthleteRequest().execute(LIST_ATHLETES_URL, ACCESS_TOKEN)

    assert response.data == json.dumps(athlete_list_response_mock, indent=4)
    mock_get.assert_called_once()
