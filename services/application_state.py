"""Module providing Enum for call status"""

from dataclasses import dataclass, field
from enum import Enum

from services.public_api import (
    AuthorizationCodeResponse,
    GetTokenResponse,
    ListAthleteResponse,
)


class Status(Enum):
    """Enum object for call status"""

    NOT_RUN = "Not Run"
    SUCCESS = "Success"
    FAILURE = "Failure"
    EXPIRED = "Expired"


@dataclass
class ApplicationState:
    # Authorization Code
    authorization_code_request_status: str = Status.NOT_RUN.value
    authorization_code_response: AuthorizationCodeResponse = field(
        default_factory=AuthorizationCodeResponse
    )
    # Token Code
    token_code_request_status: str = Status.NOT_RUN.value
    token_code_response: GetTokenResponse = field(default_factory=GetTokenResponse)
    # List Athletes
    list_athletes_request_status: str = Status.NOT_RUN.value
    list_athletes_response: ListAthleteResponse = field(
        default_factory=ListAthleteResponse
    )
    # Exception
    exception_text: str = None

    def is_authorization_complete(self) -> bool:
        return self.authorization_code_request_status == Status.SUCCESS.value

    def is_token_complete(self) -> bool:
        return self.token_code_request_status == Status.SUCCESS.value

    def is_list_athletes_complete(self) -> bool:
        return self.list_athletes_request_status == Status.SUCCESS.value
