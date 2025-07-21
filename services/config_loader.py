from dataclasses import dataclass
import configparser

@dataclass
class OAuthConfig:
    client_id: str
    client_secret: str
    authorization_url: str
    token_url: str
    scopes: str

@dataclass
class ServerConfig:
    local_port: int

    def get_local_url(self) -> str:
        return f"http://localhost:{self.local_port}"

    def get_redirect_uri(self) -> str:
        return f"http://localhost:{self.local_port}/callback"

@dataclass
class PublicApiConfig:
    list_athletes_endpoint: str
    athlete_profile_endpoint: str

class Config:
    def __init__(self, config_file: str = "./config/config.ini") -> None:
        config: configparser.ConfigParser = configparser.ConfigParser()
        config.read(config_file)

        self.oauth: OAuthConfig = OAuthConfig(
            client_id = config["oauth"]["client_id"],
            client_secret = config["oauth"]["client_secret"],
            authorization_url = config["oauth"]["authorization_url"],
            token_url = config["oauth"]["token_url"],
            scopes = config["oauth"]["scopes"]
        )

        self.server: ServerConfig = ServerConfig(
            local_port = int(config["server"]["local_port"])
        )

        self.public_api: PublicApiConfig = PublicApiConfig(
            list_athletes_endpoint = config["public_api"]["list_athletes_endpoint"],
            athlete_profile_endpoint = config["public_api"]["athlete_profile_endpoint"],
        )
