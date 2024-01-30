"""Module providing a basic OAuth2.0 implementation for use with TrainingPeaks Public API"""
import configparser
import json
import os
import time
import requests
from requests.auth import HTTPBasicAuth
from flask import Flask, request, session
from status import Status

# Read configuration
config = configparser.ConfigParser()
config.read("config.ini")

CLIENT_ID = config["oauth"]["client_id"]
CLIENT_SECRET = config["oauth"]["client_secret"]
AUTHORIZATION_URL = config["oauth"]["authorization_url"]
TOKEN_URL = config["oauth"]["token_url"]
SCOPES = config["oauth"]["scopes"]
TOKEN_REFRESH_INTERVAL = int(config["oauth"]["token_expire_sec"])

LOCAL_PORT = config["server"]["local_port"]
AUTHORIZED_URL = config["test"]["test_url"]

LOCAL_URL = f"http://localhost:{LOCAL_PORT}"
REDIRECT_URI = f"{LOCAL_URL}/callback"

app = Flask(__name__)
app.secret_key = os.urandom(24)


def get_html_response():
    """Get HTML response based on current session state"""
    return f"""
        <!DOCTYPE html>
        <html>
            <head>
                <title>Example OAuth 2.0 Authentication</title>
                <style>
                    table {{
                        width: 100%;
                        max-width: 100%
                        border-collapse: collapse;
                        text-align: left;
                        font-family: Arial, sans-serif;
                        box-shadow: 0 2px 3px rgba(0,0,0,0.1);
                    }}
                    th, td {{
                        padding: 8px;
                        border: 1px solid #ddd;
                        word-break: break-word;
                    }}
                    th {{
                        background-color: #f2f2f2;
                        color: #333;
                    }}
                    tr:nth-child(even) {{
                        background-color: #f9f9f9;
                    }}
                    tr:hover {{
                        background-color: #f1f1f1;
                    }}
                    @media screen and (max-width: 600px) {{
                        table, th, td {{
                            font-size: 0.8em;
                        }}
                    }}
                </style>
            </head>
            <body>
                {get_exception_text()}
                <table>
                    <tr>
                        <th width="25%">Step</th>
                        <th width="25%">Status</th>
                        <th width="50%">Value</th>
                    </tr>
                    <tr>
                        <td>Authorization Code Request</td>
                        <td>{session['authorization_code_request_status']}</td>
                        <td>{get_authorization_value()}</td>
                    </tr>
                    <tr>
                        <td>Token Request</td>
                        <td>{session['token_code_request_status']}</td>
                        <td>{get_token_value()}</td>
                    </tr>
                    <tr>
                        <td>Test Data Request</td>
                        <td>{session['test_data_request_status']}</td>
                        <td>{get_test_data_value()}</td>
                    </tr>
                </table>
            </body>
        </html>
    """


def initialize_session():
    """Initialize Request Statuses if not already done"""
    if "initialized" not in session:
        session["initialized"] = True
        session["authorization_code_request_status"] = Status.NOT_RUN.value
        session["token_code_request_status"] = Status.NOT_RUN.value
        session["test_data_request_status"] = Status.NOT_RUN.value


def is_authorization_code_complete():
    """Return Boolean representing whether the authorization code step is complete"""
    return session["authorization_code_request_status"] == Status.SUCCESS.value


def is_token_complete():
    """Return Boolean representing whether the token code step is complete"""
    return session["token_code_request_status"] == Status.SUCCESS.value


def is_test_data_complete():
    """Return Boolean representing whether the test data step is complete"""
    return session["test_data_request_status"] == Status.SUCCESS.value


def get_exception_text():
    """Get exception text if exists"""
    if "exception" in session:
        return session["exception"]
    return "<div />"


def reset_exception_text():
    """Clear the exception from the session"""
    session.pop("exception", None)


def set_authorization_code_exception():
    """Set the exception message for an authorization code failure"""
    session["exception"] = (
        "<h3>Authorization Falied.</h3>"
        "<p>"
        "Please double check credentials and make sure "
        "inbound traffic is permitted on the configured local port"
        "</p>"
    )


def set_token_exception():
    """Set the exception message for an token retrieval failure"""
    session["exception"] = (
        "<h3>Token Generation Failed</h3>"
        "<p>"
        "Please double check the token_url and credentials in the config"
        "</p>"
    )


def set_test_data_exception(status_code, body):
    """Set the exception message for an test data call failure"""
    session["exception"] = (
        f"<h3>Test Data Request Failed</h3>"
        f"<p>Status: {status_code}</p>"
        f"<p>Body: {body}</p>"
    )


def get_authorization_value():
    """Get the the HTML for the Value column of the Authoization Code Row"""
    if is_authorization_code_complete():
        return session["authorization_code"]
    # [IMPORTANT EXAMPLE] - LINK TO GET AUTHORIZATION CODE FROM TP
    auth_url = (
        f"{AUTHORIZATION_URL}?response_type=code"
        f"&client_id={CLIENT_ID}"
        f"&redirect_uri={REDIRECT_URI}"
        f"&scope={SCOPES}"
    )
    return f'<a href="{auth_url}">Authorize</a>'


def get_token_value():
    """Get a HTML Link to the Get Token endpoint"""
    if not is_authorization_code_complete():
        return "<div />"
    if is_token_expired():
        return f'<a href="{LOCAL_URL}/refresh-token">Refresh Token</a>'
    if is_token_complete():
        human_readable_expire = time.strftime(
            "%Y-%m-%d %H:%M:%S", 
            time.gmtime(session["access_token_expire"])
        )
        return (
            f'''
            {{ <br />
                "Token": "{session["access_token"]}",<br />
                "Refresh Token": "{session["refresh_token"]}",<br />
                "Token Expiration": "{human_readable_expire}"<br />
            }}<br />
            <a href="{LOCAL_URL}/refresh-token">Refresh Token</a>
            '''
        )
    return f'<a href="{LOCAL_URL}/get-token">Get Token</a>'


def get_test_data_value():
    """Get a HTML Link to Get Test Data endpoint"""
    if ((not is_authorization_code_complete())
        or (not is_token_complete())
        or is_token_expired()
    ):
        return "<div />"
    if is_test_data_complete():
        return session["test_data"]
    return f'<a href="{LOCAL_URL}/get-test-data">Make Example Call</a>'


def is_token_expired():
    """Get boolean whether the current Access Token is expired"""
    if not is_token_complete():
        return False
    if session["access_token_expire"] > time.time():
        return False
    session['token_code_request_status'] = Status.EXPIRED.value
    return True


@app.route("/")
def home():
    """Entrypoint of the Application"""
    initialize_session()
    return get_html_response()


@app.route("/callback")
def callback():
    """Handle callback from Authorization call"""
    initialize_session()
    # [IMPORTANT EXAMPLE] - HANDLE CALLBACK
    if "code" not in request.args:
        session["authorization_code_request_status"] = Status.FAILURE.value
        set_authorization_code_exception()
    else:
        reset_exception_text()
        session["authorization_code_request_status"] = Status.SUCCESS.value
        session["authorization_code"] = request.args.get("code")
    return get_html_response()


@app.route("/get-token")
def get_token():
    """Use the Authoization Code to get an Access Token"""
    initialize_session()
    if not is_authorization_code_complete():
        return get_html_response()
    # [IMPORTANT EXAMPLE] - GET TOKEN
    token_data = {
        "grant_type": "authorization_code",
        "code": session["authorization_code"],
        "redirect_uri": REDIRECT_URI,
    }
    headers = {"Accept": "application/json"}
    response = requests.post(
        TOKEN_URL,
        data=token_data,
        headers=headers,
        auth=HTTPBasicAuth(CLIENT_ID, CLIENT_SECRET),
        timeout=6000,
    )
    if response.ok:
        session["token_code_request_status"] = Status.SUCCESS.value
        session["access_token"] = response.json().get("access_token")
        session["refresh_token"] = response.json().get("refresh_token")
        session["access_token_expire"] = time.time() + int(response.json().get("expires_in"))
    else:
        session["token_code_request_status"] = Status.FAILURE.value
        set_token_exception()
    return get_html_response()


@app.route("/refresh-token")
def refresh_token():
    """Use the Refresh Token to get a new Access Token"""
    initialize_session()
    if not is_authorization_code_complete() or not is_token_complete():
        return get_html_response()
    # [IMPORTANT EXAMPLE] - TOKEN REFRESH
    token_data = {
        "grant_type": "refresh_token",
        "refresh_token": session["refresh_token"],
    }
    headers = {"Accept": "application/json"}
    response = requests.post(
        TOKEN_URL,
        data=token_data,
        headers=headers,
        auth=HTTPBasicAuth(CLIENT_ID, CLIENT_SECRET),
        timeout=6000,
    )
    if response.ok:
        session["token_code_request_status"] = Status.SUCCESS.value
        session["access_token"] = response.json().get("access_token")
        session["refresh_token"] = response.json().get("refresh_token")
        session["access_token_expire"] = time.time() + int(response.json().get("expires_in"))
    else:
        session["token_code_request_status"] = Status.FAILURE.value
        set_token_exception()
    return get_html_response()


@app.route("/get-test-data")
def get_data():
    """Makes a GET request using the obtained token"""
    initialize_session()
    if not is_authorization_code_complete() or not is_token_complete():
        return get_html_response()
    # [IMPORTANT EXAMPLE] - GET TEST DATA
    headers = {"Authorization": f"Bearer {session['access_token']}"}
    response = requests.get(AUTHORIZED_URL, headers=headers, timeout=6000)
    if response.ok:
        reset_exception_text()
        session["test_data"] = json.dumps(response.json(), indent=4)
        session["test_data_request_status"] = Status.SUCCESS.value
    else:
        session["test_data_request_status"] = Status.FAILURE.value
        set_test_data_exception(response.status_code, response.raw)
    return get_html_response()


if __name__ == "__main__":
    app.run(port=LOCAL_PORT)
    session["authorization_code_request_status"] = Status.NOT_RUN.value
    session["token_code_request_status"] = Status.NOT_RUN.value
    session["test_data_request_status"] = Status.NOT_RUN.value
