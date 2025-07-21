from dataclasses import dataclass, field
import time
from services.application_state import ApplicationState
from services.config_loader import Config

@dataclass
class HtmlRenderer:
    config: Config
    state: ApplicationState = field(default_factory=ApplicationState)

    def get_auth_link(self, authorization_url, client_id, redirect_uri, scopes):
        auth_url = (
            f"{authorization_url}?response_type=code"
            f"&client_id={client_id}"
            f"&redirect_uri={redirect_uri}"
            f"&scope={scopes}"
        )
        return f'<a href="{auth_url}">Authorize</a>'
    
    def get_authorization_value(self):
        """Get the the HTML for the Value column of the Authoization Code Row"""
        if self.state.is_authorization_complete():
            return self.state.authorization_code_response.authorization_code
        return self.get_auth_link(
            self.config.oauth.authorization_url,
            self.config.oauth.client_id,
            self.config.server.get_redirect_uri(),
            self.config.oauth.scopes
        )

    def get_token_value(self):
        """Get a HTML Link to the Get Token endpoint"""
        if not self.state.is_authorization_complete():
            return ""
        if not self.state.is_token_complete():
            return f'<a href="{self.config.server.get_local_url()}/get-token">Get Token</a>'
        if self.state.token_code_response.is_token_expired():
            return f'<a href="{self.config.server.get_local_url()}/refresh-token">Refresh Token</a>'

        human_readable_expire = time.strftime(
            "%Y-%m-%d %H:%M:%S", 
            time.gmtime(self.state.token_code_response.access_token_expire)
        )
        return (
            f'''
            {{ <br />
                "Token": "{self.state.token_code_response.access_token}",<br /><br />
                "Refresh Token": "{self.state.token_code_response.refresh_token}",<br /><br />
                "Token Expiration": "{human_readable_expire}"<br /><br />
            }}<br />
            <a href="{self.config.server.get_local_url()}/refresh-token">Refresh Token</a>
            '''
        )

    def get_list_athletes_value(self):
        """Get a HTML Link to List Athletes endpoint"""
        if not self.state.is_authorization_complete():
            return ""
        if not self.state.is_token_complete():
            return ""
        if self.state.token_code_response.is_token_expired():
            return "Token Expired, Refresh Token."
        if not self.state.is_list_athletes_complete():
            return f'<a href="{self.config.server.get_local_url()}/get-test-data">Make Example Call</a>'
        return self.state.list_athletes_response.data

    def get_athlete_profile_value(self):
        """Get a HTML Link to Athlete Profile endpoint"""
        if not self.state.is_authorization_complete():
            return ""
        if not self.state.is_token_complete():
            return ""
        if self.state.token_code_response.is_token_expired():
            return "Token Expired, Refresh Token."
        if not self.state.is_athlete_profile_complete():
            return f'<a href="{self.config.server.get_local_url()}/get-test-data">Make Example Call</a>'
        return self.state.athlete_profile_response.data

    def set_authorization_exception(self):
        self.state.exception_text = (
        "<h3>Authorization Falied.</h3>"
        "<p>"
        "Please double check credentials and make sure "
        "inbound traffic is permitted on the configured local port"
        "</p>"
    )

    def set_token_exception(self):
        self.state.exception_text = (
            "<h3>Token Generation Failed</h3>"
            "<p>"
            "Please double check the token_url and credentials in the config"
            "</p>"
        )

    def set_token_expired_exception(self):
        self.state.exception_text = (
            "<h3>Token Expired</h3>"
            "<p>"
            "Your Token has Expired, please refresh your token"
            "</p>"
        )

    def set_list_athlete_exception(self, status_code, body):
        self.state.exception_text = (
            f"<h3>List Athlete Request Failed</h3>"
            f"<p>Status: {status_code}</p>"
            f"<p>Body: {body}</p>"
        )

    def set_athlete_profile_exception(self, status_code, body):
        self.state.exception_text = (
            f"<h3>Athlete Profile Request Failed</h3>"
            f"<p>Status: {status_code}</p>"
            f"<p>Body: {body}</p>"
        )

    def clear_exceptions(self):
        self.state.exception_text = ""

    def render(self):
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
                    {self.state.exception_text}
                    <table>
                        <tr>
                            <th width="25%">Step</th>
                            <th width="25%">Status</th>
                            <th width="50%">Value</th>
                        </tr>
                        <tr>
                            <td>Authorization Code Request</td>
                            <td>{self.state.authorization_code_request_status}</td>
                            <td>{self.get_authorization_value()}</td>
                        </tr>
                        <tr>
                            <td>Token Request</td>
                            <td>{self.state.token_code_request_status}</td>
                            <td>{self.get_token_value()}</td>
                        </tr>
                        <tr>
                            <td>List Athletes Request</td>
                            <td>{self.state.list_athletes_request_status}</td>
                            <td>{self.get_list_athletes_value()}</td>
                        </tr>
                        <tr>
                            <td>Athlete Profile Request</td>
                            <td>{self.state.athlete_profile_request_status}</td>
                            <td>{self.get_athlete_profile_value()}</td>
                        </tr>
                    </table>
                </body>
            </html>
        """
    