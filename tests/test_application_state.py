import pytest
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from services.application_state import ApplicationState, Status

def test_initial_state():
    app_state = ApplicationState()
    
    assert app_state.authorization_code_request_status == Status.NOT_RUN.value
    assert app_state.token_code_request_status == Status.NOT_RUN.value
    assert app_state.list_athletes_request_status == Status.NOT_RUN.value
    assert app_state.exception_text is None

def test_is_authorization_complete():
    app_state = ApplicationState()
    app_state.authorization_code_request_status = Status.SUCCESS.value
    assert app_state.is_authorization_complete() is True

    app_state.authorization_code_request_status = Status.FAILURE.value
    assert app_state.is_authorization_complete() is False

def test_is_token_complete():
    app_state = ApplicationState()
    app_state.token_code_request_status = Status.SUCCESS.value
    assert app_state.is_token_complete() is True

    app_state.token_code_request_status = Status.FAILURE.value
    assert app_state.is_token_complete() is False

def test_is_list_athletes_complete():
    app_state = ApplicationState()
    app_state.list_athletes_request_status = Status.SUCCESS.value
    assert app_state.is_list_athletes_complete() is True

    app_state.list_athletes_request_status = Status.FAILURE.value
    assert app_state.is_list_athletes_complete() is False
