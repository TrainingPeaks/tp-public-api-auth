# OAuth2.0 Implementation for TrainingPeaks Public API

## Introduction
This Python module provides a basic implementation of OAuth 2.0 for interfacing with the TrainingPeaks Public API. It allows users to authenticate, receive access tokens, and make authorized API calls.

## Requirements
- Python 3.x
- Flask
- Requests

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
1. Copy the appropriate example configuration file to `config.ini`.
- `cp config.ini.prod.example config.ini`
or
- `cp config.ini.sandbox.example config.ini`

2. Edit `config.ini` to include your `client_id`, `client_secret`, and `scopes` as well as the `test_url` if needed. 

## Usage
The module allows you to:
- Initiate the authorization process via an HTML link
- Handle the callback from the authorization process
- Retrieve and use access tokens to make authorized API calls

## Running the Application
To run the application, use the following command:
`python app.py`
The application will start a local server (default port 8080), where you can interact with the OAuth2.0 implementation.

## Endpoints
- `/`: The home page, which provides the authorization link.
- `/callback`: The callback endpoint for handling the response from TrainingPeaks.
- `/get-data`: An example endpoint that makes an authorized API call using the obtained token.

## Contributing
Contributions to the project are welcome. Please ensure that your code adheres to the project's standards and submit a pull request for review.