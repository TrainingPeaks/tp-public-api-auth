"""Module providing a basic OAuth2.0 implementation for use with TrainingPeaks Public API"""
import configparser
import json
import os
import time
import requests
from requests.auth import HTTPBasicAuth
from flask import Flask, Response, request, session

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

def get_authorization_link():
    """Get the HTML link to initialize Authorization"""
    auth_url = (
        f"{AUTHORIZATION_URL}?response_type=code"
        f"&client_id={CLIENT_ID}"
        f"&redirect_uri={REDIRECT_URI}"
        f"&scope={SCOPES}"
    )
    return f'<a href="{auth_url}">Authorize</a>'

def get_access_token():
    """Use the Authoization Code to get an Access Token"""
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
    if not response.ok:
        return False
    session["access_token"] = response.json().get("access_token")
    session["access_token_expire"] = time.time() + TOKEN_REFRESH_INTERVAL
    return True

def session_has_valid_token():
    """Get a Boolean representing whether the session contains a valid token"""
    if "access_token" not in session:
        return False
    if "access_token_expire" not in session:
        return False
    if session["access_token_expire"] < time.time():
        return False
    return True

@app.route("/")
def home():
    """Entrypoint of the Application"""
    if "access_token" not in session:
        return get_authorization_link()
    return f'<a href="{LOCAL_URL}/get-data">Make Example Call</a>'


@app.route("/callback")
def callback():
    """Handle callback from Authorization call"""
    if "code" not in request.args:
        return (
            "<h3>Authorization Falied.</h3>"
            "<p>"
            "Please double check credentials and make sure "
            "inbound traffic is permitted on the configured local port"
            "</p>"
        )
    access_token = request.args.get("code")
    session["authorization_code"] = access_token
    return (
        f"<h3>Access Token Generated Successfully!</h3>"
        f'<a href="{LOCAL_URL}/get-data">Make Example Call</a>'
    )


@app.route("/get-data")
def get_data():
    """Makes a GET request using the obtained token"""
    if 'authorization_code' not in session:
        return get_authorization_link()
    if not session_has_valid_token():
        if not get_access_token():
            return (
                "<h3>Token Generation Failed</h3>"
                "<p>"
                "Please double check the token_url in the config"
                "</p>"
            )
    headers = {"Authorization": f"Bearer {session['access_token']}"}
    response = requests.get(AUTHORIZED_URL, headers=headers, timeout=6000)
    if response.ok:
        return Response(json.dumps(response.json(), indent=4), content_type='application/json')
    return (
        f"<h3>Example Request Failed</h3>"
        f"<p>Status: {response.status_code}</p>"
        f"<p>Body: {response.raw}</p>"
    )
if __name__ == "__main__":
    app.run(port=LOCAL_PORT)
