#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A script to download video files from Gamechanger
"""

import os
import time

import m3u8
import requests

from datetime import datetime

from gamechanger_client import GameChangerClient
from tqdm import tqdm


class RequestsClient:

    def __init__(self, cookies):
        self.cookies = cookies

    def download(self, uri, timeout=None, headers=None, verify_ssl=True):
        """Download helper used by m3u8 (returns text and final URL).

        Args:
            uri (str): URL to fetch.
            timeout (float|tuple|None): requests timeout.
            headers (dict|None): optional headers.
            verify_ssl (bool): whether to verify TLS certs.

        Returns:
            tuple: (response_text, final_url)
        """
        if headers is None:
            headers = {}

        resp = requests.get(uri, timeout=timeout, headers=headers, cookies=self.cookies, verify=verify_ssl)
        resp.raise_for_status()
        return resp.text, resp.url


def main():
    gamechanger = GameChangerClient()

    # Get current teams and sort by created date
    teams = gamechanger.me.teams()
    teams.sort(key=lambda x: x['created_at'], reverse=True)

    # Allow user to select a team
    i = 1
    print('Select a team:')
    for team in teams:
        print(f"[{i}] {team['name']}")
        i += 1
    team_index = int(input('Which team? '))
    team_id = teams[team_index - 1]['id']

    # Get the team's schedule and filter by games with a start time
    schedule = gamechanger.teams.schedule(team_id)
    game_schedule = list(filter(lambda x: (x['event']['event_type'] == 'game'
                                           and x['event']['status'] == 'scheduled'
                                           and 'datetime' in x['event']['start'].keys()), schedule))

    # Allow user to select an event
    while True:
        i = 1
        print('\nSelect a game to download:')
        for game in game_schedule:
            game_date = datetime.fromisoformat(game['event']['start']['datetime'][:-1] + '+00:00')
            game_date = game_date.astimezone(tz=None).strftime('%Y-%m-%d %I:%M%p')
            print(f"[{i}] {game_date} {game['event']['title']}")
            i += 1
        event_index = int(input('Which event should we check? '))
        event_id = game_schedule[event_index - 1]['event']['id']

        try:
            # Check to see if there are any videos for a given event
            gamechanger.teams.event_video_stream_assets(team_id, event_id)

            # Get the video stream playback info for the selected event
            video_stream_playback_info = gamechanger.teams.event_video_stream_playback_info(team_id, event_id)
            break
        except Exception:
            print('\n---  Failed Fetching Video Streams For Selected Event  ---')
            print("--- Either there are none, or you don't have permisson ---")
            print('---              Please Try Another Event              ---\n')
            time.sleep(2)

    # Make a directory for our videos to reside in - remove old files if they exist
    video_directory = f"./videos/{game_schedule[event_index - 1]['event']['id']}"
    if os.path.isdir(video_directory):
        for filename in os.listdir(video_directory):
            filepath = os.path.join(video_directory, filename)
            os.remove(filepath)
    os.makedirs(video_directory, exist_ok=True)

    video_stream_count = 1
    for video_stream in video_stream_playback_info:

        cookies = video_stream['cookies']
        video_assets_url = video_stream['url']

        video_request_client = RequestsClient(cookies)

        # Get the manifest of all available streams
        m3u8_data = m3u8.load(video_assets_url, http_client=video_request_client)

        # Get the highest available resolution
        playlist_uri = None
        playlist_bandwidth = 0
        if m3u8_data.is_variant:
            for playlist in m3u8_data.playlists:
                if playlist.stream_info.bandwidth > playlist_bandwidth:
                    playlist_bandwidth = playlist.stream_info.bandwidth
                    playlist_uri = playlist.uri

        # Get the variant playlist
        playlist_uri = f"{'/'.join(m3u8_data.base_uri.split('/')[:-2])}/{playlist_uri}"
        m3u8_data = m3u8.load(playlist_uri, http_client=video_request_client)

        # If there's an init segment, download it
        for segmap in m3u8_data.segment_map:
            init_uri = f"{'/'.join(m3u8_data.base_uri.split('/')[:-2])}/{segmap.uri}"
            extension = os.path.splitext(segmap.uri)[1]
            with open(f'{video_directory}/stream_{video_stream_count}{extension}', 'ab') as video_file:
                with requests.get(init_uri, cookies=cookies, stream=True) as r:
                    r.raise_for_status()
                    video_file.write(r.content)

        # Download and merge the video segments
        for segment_file in tqdm(m3u8_data.files):
            video_uri = f"{'/'.join(m3u8_data.base_uri.split('/')[:-2])}/{segment_file}"

            extension = os.path.splitext(video_uri)[1]
            with open(f'{video_directory}/stream_{video_stream_count}{extension}', 'ab') as video_file:
                with requests.get(video_uri, cookies=cookies, stream=True) as r:
                    r.raise_for_status()
                    for chunk in r.iter_content(chunk_size=8192):
                        if chunk:
                            video_file.write(chunk)

        video_stream_count += 1


if __name__ == '__main__':
    main()
