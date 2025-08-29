from dataclasses import asdict, dataclass
import json
import time
import requests
from requests.auth import HTTPBasicAuth

@dataclass
class AuthorizationCodeResponse:
    authorization_code: str = ""

@dataclass
class GetTokenResponse:
    refresh_token: str = ""
    access_token: str = ""
    access_token_expire: int = -1

    def is_token_expired(self):
        return False if self.access_token_expire > time.time() else True

@dataclass
class GetTokenRequest:
    code: str
    redirect_uri: str = "http://localhost:8080/callback"
    grant_type: str = "authorization_code"

    def execute(self, token_url: str, client_id: str, client_secret: str) -> GetTokenResponse:
        body = {
            "grant_type": self.grant_type,
            "code": self.code,
            "redirect_uri": self.redirect_uri,
            "client_id": client_id,
            "client_secret": client_secret,
        }
        response: requests.Response = requests.post(
            token_url,
            data=body,
            headers={"Accept": "application/json"},
            timeout=120,
        )
        return None if not response.ok else GetTokenResponse(
            refresh_token = response.json().get("refresh_token"),
            access_token = response.json().get("access_token"),
            access_token_expire = time.time() + int(response.json().get("expires_in"))
        )

@dataclass
class RefreshTokenRequest:
    refresh_token: str
    grant_type: str = "refresh_token"

    def execute(self, token_url, client_id, client_secret):
        response: requests.Response = requests.post(
            token_url,
            data=asdict(self),
            headers={"Accept": "application/json"},
            auth=HTTPBasicAuth(client_id, client_secret),
            timeout=120,
        )
        return None if not response.ok else GetTokenResponse(
            refresh_token = response.json().get("refresh_token"),
            access_token = response.json().get("access_token"),
            access_token_expire = time.time() + int(response.json().get("expires_in"))
        )

@dataclass
class ListAthleteResponse:
    data: str = ""
    status_code: int = -1
    message: str = ""

@dataclass
class ListAthleteRequest:
    def execute(self, list_athlete_url: str, access_token: str) -> ListAthleteResponse:
        response: requests.Response = requests.get(
            list_athlete_url,
            headers={"Authorization": f"Bearer {access_token}"},
            timeout=120
        )

        return None if not response.ok else ListAthleteResponse(
            data = json.dumps(response.json(), indent=4),
            status_code = response.status_code,
            message = response.raw
        )
