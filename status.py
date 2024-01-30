"""Module providing Enum for call status"""
from enum import Enum

class Status(Enum):
    """Enum object for call status"""
    NOT_RUN = "Not Run"
    SUCCESS = "Success"
    FAILURE = "Failure"
    EXPIRED = "Expired"
