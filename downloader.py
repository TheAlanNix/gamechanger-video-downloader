#!/bin/python/env
# -*- coding: utf-8 -*-
"""
A script to download video files from Gamechanger
"""

import os
import time

import m3u8
import requests

from datetime import datetime

from tqdm import tqdm

from gamechanger import GameChangerDownloader, ApiError


class RequestsClient():

    def __init__(self, cookies):
        self.cookies = cookies

    def download(self, uri, timeout=None, headers={}, verify_ssl=True):
        o = requests.get(uri, timeout=timeout, headers=headers, cookies=self.cookies)
        return o.text, o.url


def main():
    gamechanger_downloader = GameChangerDownloader()

    # Get current teams and sort by created date
    teams = gamechanger_downloader.get_teams()
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
    schedule = gamechanger_downloader.get_team_schedule(team_id)
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
            gamechanger_downloader.get_event_video_steam_videos(team_id, event_id)

            # Get the video stream playback info for the selected event
            video_stream_playback_info = gamechanger_downloader.get_event_video_stream_playback_info(team_id, event_id)
            break
        except ApiError:
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

        print(f'\nFetching video {video_stream_count} of {len(video_stream_playback_info)}')

        # Download and merge the videos
        with open(f'{video_directory}/stream_{video_stream_count}.ts', 'ab') as ts_file:
            for file in tqdm(m3u8_data.files):
                video_uri = f"{'/'.join(m3u8_data.base_uri.split('/')[:-2])}/{file}"

                with requests.get(video_uri, cookies=cookies, stream=True) as r:
                    for chunk in r.iter_content(chunk_size=8192):
                        ts_file.write(chunk)

        video_stream_count += 1


if __name__ == '__main__':
    main()
