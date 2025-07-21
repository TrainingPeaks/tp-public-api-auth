"""Module providing a basic OAuth2.0 implementation for use with TrainingPeaks Public API"""

import os
from flask import Flask, request
from services.config_loader import Config
from services.application_state import Status
from services.html_renderer import HtmlRenderer
from services.public_api import (
    AuthorizationCodeResponse,
    GetTokenRequest,
    GetTokenResponse,
    ListAthleteRequest,
    ListAthleteResponse,
    AthleteProfileRequest,
    AthleteProfileResponse,
    RefreshTokenRequest,
)

app = Flask(__name__)
app.secret_key = os.urandom(24)
config: Config = Config()
html_renderer = HtmlRenderer(config=config)


@app.route("/")
def home():
    """Entrypoint of the Application"""
    return html_renderer.render()


@app.route("/callback")
def callback():
    """Handle callback from Authorization call"""
    if "code" not in request.args:
        html_renderer.state.authorization_code_request_status = Status.FAILURE.value
        html_renderer.set_authorization_exception()
    else:
        html_renderer.clear_exceptions()
        html_renderer.state.authorization_code_request_status = Status.SUCCESS.value
        html_renderer.state.authorization_code_response = AuthorizationCodeResponse(
            authorization_code=request.args.get("code")
        )
    return html_renderer.render()


@app.route("/get-token")
def get_token():
    """Use the Authoization Code to get an Access Token"""
    if not html_renderer.state.is_authorization_complete():
        return html_renderer.render()
    response: GetTokenResponse = GetTokenRequest(
        html_renderer.state.authorization_code_response.authorization_code,
        config.server.get_redirect_uri()
    ).execute(
        config.oauth.token_url, 
        config.oauth.client_id, 
        config.oauth.client_secret
    )

    if response:
        html_renderer.clear_exceptions()
        html_renderer.state.token_code_request_status = Status.SUCCESS.value
        html_renderer.state.token_code_response = response
    else:
        html_renderer.state.token_code_request_status = Status.FAILURE.value
        html_renderer.set_token_exception()
    return html_renderer.render()


@app.route("/refresh-token")
def refresh_token():
    """Use the Refresh Token to get a new Access Token"""
    if (
        not html_renderer.state.is_authorization_complete()
        or not html_renderer.state.is_token_complete()
    ):
        return html_renderer.render()

    response: GetTokenResponse = RefreshTokenRequest(
        html_renderer.state.token_code_response.refresh_token
    ).execute(config.oauth.token_url, config.oauth.client_id, config.oauth.client_secret)

    if response:
        html_renderer.clear_exceptions()
        html_renderer.state.token_code_request_status = Status.SUCCESS.value
        html_renderer.state.token_code_response = response
    else:
        html_renderer.state.token_code_request_status = Status.FAILURE.value
        html_renderer.set_token_exception()
    return html_renderer.render()


@app.route("/get-test-data")
def get_data():
    """Makes a GET request using the obtained token"""
    if (
        not html_renderer.state.is_authorization_complete()
        or not html_renderer.state.is_token_complete()
    ):
        return html_renderer.render()

    if html_renderer.state.token_code_response.is_token_expired():
        html_renderer.state.token_code_request_status = Status.EXPIRED.value
        html_renderer.set_token_expired_exception()
        return html_renderer.render()

    response: AthleteProfileResponse = AthleteProfileRequest().execute(
        config.public_api.athlete_profile_endpoint,
        html_renderer.state.token_code_response.access_token,
    )

    if response:
        html_renderer.clear_exceptions()
        html_renderer.state.athlete_profile_request_status = Status.SUCCESS.value
        html_renderer.state.athlete_profile_response = response
    else:
        html_renderer.state.athlete_profile_request_status = Status.FAILURE.value
        html_renderer.set_athlete_profile_exception(response.status_code, response.message)
    return html_renderer.render()

# """Makes a GET request using the obtained token"""
    # if (
    #     not html_renderer.state.is_authorization_complete()
    #     or not html_renderer.state.is_token_complete()
    # ):
    #     return html_renderer.render()
    #
    # if html_renderer.state.token_code_response.is_token_expired():
    #     html_renderer.state.token_code_request_status = Status.EXPIRED.value
    #     html_renderer.set_token_expired_exception()
    #     return html_renderer.render()
    #
    # response: ListAthleteResponse = ListAthleteRequest().execute(
    #     config.public_api.list_athletes_endpoint,
    #     html_renderer.state.token_code_response.access_token,
    # )
    #
    # if response:
    #     html_renderer.clear_exceptions()
    #     html_renderer.state.list_athletes_request_status = Status.SUCCESS.value
    #     html_renderer.state.list_athletes_response = response
    # else:
    #     html_renderer.state.list_athletes_request_status = Status.FAILURE.value
    #     html_renderer.set_list_athlete_exception(response.status_code, response.message)
    # return html_renderer.render()
    #

if __name__ == "__main__":
    app.run(port=config.server.local_port)
