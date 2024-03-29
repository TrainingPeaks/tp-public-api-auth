# OAuth2.0 Implementation for TrainingPeaks Public API

## Introduction
This Python module provides a basic implementation of OAuth 2.0 for interfacing with the TrainingPeaks Public API. It allows users to authenticate, receive access tokens, and make authorized API calls.

## Installation
Clone the repository and install the required Python packages.
- `git clone git@github.com:TrainingPeaks/tp-public-api-auth.git`
- `cd tp-public-api-auth`
- `pip install -r requirements.txt`

## Configuration
The module uses a `config.ini` file for configuration. Two example configuration files are provided:
- `config.ini.prod.example` for production
- `config.ini.sandbox.example` for sandbox/testing

To configure the application:
1. Copy the appropriate example configuration file to `config/config.ini`.
- `cp config/config.ini.prod.example config/config.ini`
or
- `cp config/config.ini.sandbox.example config/config.ini`

1. Edit `config.ini` to include your `client_id`, `client_secret`, and `scopes`. 

## Usage
The module allows you to:
- Initiate the authorization process via an HTML link
- Handle the callback from the authorization process
- Retrieve and use access tokens to make authorized API calls

## Running the Application
To run the application, use the following command:
`python app/main.py`
The application will start a local server (default port 8080), where you can interact with the OAuth2.0 implementation.

## Testing the Application
To run the application tests, use the following command:
`pytest`

## Endpoints
- `/`: The home page, which provides the authorization link.
- `/callback`: The callback endpoint which will be called once TrainingPeaks has been authorized
- `/get-token`: Get a token using the Authorization Code supplied by the `/callback` endpoint
- `/refresh-token`: Refresh the token using the Refresh Token supplied from `get-token` endpoint
- `/get-test-data`: Get the test data using the Token provide by `get-token` or `refresh-token`

## Contributing
Contributions to the project are welcome. Please ensure that your code adheres to the project's standards and submit a pull request for review.