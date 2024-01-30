import sys
import os
import time
import unittest
import json
from unittest.mock import patch, MagicMock
from flask_testing import TestCase
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.status import Status
from app.main import app


class TestOAuthApp(TestCase):
    # Setting up the Flask test client
    def create_app(self):
        app.config['TESTING'] = True
        return app

    def setUp(self):
        self.client = app.test_client()

    def tearDown(self):
        pass

    # Testing '/' route
    def test_home_route(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    # Testing '/callback' route
    def test_callback_route(self):
        response = self.client.get('/callback', query_string={'code': 'testcode'})
        with self.client.session_transaction() as session:
            self.assertEqual(session['authorization_code_request_status'], Status.SUCCESS.value)
            self.assertEqual(session['authorization_code'], 'testcode')

    # Testing '/get-token' route with a mocked response
    @patch('requests.post')
    def test_get_token_route(self, mock_post):
        mock_response = MagicMock()
        mock_response.ok = True
        mock_response.json.return_value = {
            "access_token": "test_access_token",
            "refresh_token": "test_refresh_token",
            "expires_in": 3600
        }
        mock_post.return_value = mock_response

        with self.client.session_transaction() as session:
            session['initialized'] = True
            session['authorization_code'] = 'testcode'
            session['authorization_code_request_status'] = Status.SUCCESS.value
            session['test_data_request_status'] = Status.NOT_RUN.value


        response = self.client.get('/get-token')
        self.assertEqual(response.status_code, 200)

        with self.client.session_transaction() as session:
            self.assertEqual(session['token_code_request_status'], Status.SUCCESS.value)
            self.assertEqual(session['access_token'], 'test_access_token')

    # Testing '/refresh-token' route with a mocked response
    @patch('requests.post')
    def test_refresh_token_route(self, mock_post):
        mock_response = MagicMock()
        mock_response.ok = True
        mock_response.json.return_value = {
            "access_token": "new_access_token",
            "refresh_token": "new_refresh_token",
            "expires_in": 3600
        }
        mock_post.return_value = mock_response

        with self.client.session_transaction() as session:
            session['initialized'] = True
            session['authorization_code'] = 'testcode'
            session['authorization_code_request_status'] = Status.SUCCESS.value
            session['token_code_request_status'] = Status.SUCCESS.value
            session['refresh_token'] = 'test_refresh_token'
            session['test_data_request_status'] = Status.NOT_RUN.value

            

        response = self.client.get('/refresh-token')
        self.assertEqual(response.status_code, 200)

        with self.client.session_transaction() as session:
            self.assertEqual(session['token_code_request_status'], Status.SUCCESS.value)
            self.assertEqual(session['access_token'], 'new_access_token')

    # Testing '/get-test-data' route with a mocked response
    @patch('requests.get')
    def test_get_test_data_route(self, mock_get):
        test_data = {"data": "test"}
        mock_response = MagicMock()
        mock_response.ok = True
        mock_response.json.return_value = test_data
        mock_get.return_value = mock_response

        with self.client.session_transaction() as session:
            session['initialized'] = True
            session['access_token_expire'] = time.time() + 6000
            session['authorization_code'] = 'testcode'
            session['access_token'] = 'testtoken'
            session['refresh_token'] = 'testrefreshtoken'
            session['authorization_code_request_status'] = Status.SUCCESS.value
            session['token_code_request_status'] = Status.SUCCESS.value

        response = self.client.get('/get-test-data')
        self.assertEqual(response.status_code, 200)

        with self.client.session_transaction() as session:
            self.assertEqual(session['test_data_request_status'], Status.SUCCESS.value)
            self.assertEqual(json.loads(session['test_data']), test_data)


if __name__ == '__main__':
    unittest.main()
