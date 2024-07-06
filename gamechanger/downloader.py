# -*- coding: utf-8 -*-
"""
Downloader class.
"""

import json
import logging
import os
import uuid

import requests

from .config import (
    DEFAULT_BASE_DOMAIN,
    DEFAULT_SUCCESS_RESPONSE_CODES
)
from .exceptions import ApiError
from .version import __version__  # noqa: F401

logger = logging.getLogger(__name__)


class GameChangerDownloader:

    def __init__(self,
                 username=None,
                 password=None,
                 token=None):

        self._base_url = f'https://{DEFAULT_BASE_DOMAIN}'

        self._username = username or os.getenv('GC_USERNAME')
        self._password = password or os.getenv('GC_PASSWORD')
        self._token = token or os.getenv('GC_TOKEN')

        self._client_id = uuid.uuid1()

        # Create a new requests session
        self._session = requests.Session()

    def _post(self, uri, headers=None, data=None, **kwargs):
        response = self._session.request('POST', uri, json=data, **kwargs)
        return response

    def _check_response_code(self, response, expected_response_codes):
        """
        Check the requests.response.status_code to make sure it's one that we expected.
        """

        if response.status_code in expected_response_codes:
            pass
        else:
            raise ApiError(response)

    def _request(self, method, uri, **kwargs):
        """
        A method to abstract building requests to GameChanger.

        Args:
            method (str): The HTTP request method ("GET", "POST", ...)
            uri (str): The URI of the API endpoint
            kwargs (Any): passed on to the requests package

        Returns:
            requests.models.Response: a Requests response object

        Raises:
             ApiError if anything but expected response code is returned
        """

        headers = self._get_request_headers()

        # Check for 'data' or 'json'
        data = kwargs.get('data', '')
        json = kwargs.get('json', '')
        if data or json:
            logger.debug(f'{method} request data:\nData: {data}\nJSON: {json}')

        # Make the HTTP request to the API endpoint
        response = self._session.request(method, uri, headers=headers, **kwargs)

        # Validate the response
        self._check_response_code(response, DEFAULT_SUCCESS_RESPONSE_CODES)

        # self._print_debug_response(response)

        return response

    def _get_request_headers(self):
        """
        A method to build HTTP request headers for GameChanger.
        """

        # Build the request headers
        headers = self._session.headers

        headers['gc-token'] = self._token
        headers['user-agent'] = 'gamechanger-python-client'

        logger.debug('Request headers: \n' + json.dumps(dict(headers), indent=2))

        return headers

    def auth(self):
        auth_url = f'{self._base_url}/auth'

        response = self._session.options(auth_url)
        print(response.text)
        exit()

    def get_teams(self):
        return self._request('GET', f'{self._base_url}/me/teams').json()

    def get_team_schedule(self, team_id):
        return self._request('GET', f'{self._base_url}/teams/{team_id}/schedule').json()

    def get_team_clips(self, team_id):
        return self._request('GET', f'{self._base_url}/clips?kind=event&teamId={team_id}').json()

    def get_event_video_steam_assets(self, team_id, event_id):
        return self._request('GET', f'{self._base_url}/teams/{team_id}/schedule/events/{event_id}/video-stream/assets').json()

    def get_event_video_steam_videos(self, team_id, event_id):
        return self._request('GET', f'{self._base_url}/teams/{team_id}/schedule/events/{event_id}/video-stream/assets').json()

    def get_event_video_stream_playback_info(self, team_id, event_id):
        return self._request('GET', f'{self._base_url}/teams/{team_id}/schedule/events/{event_id}/video-stream/assets/playback').json()
