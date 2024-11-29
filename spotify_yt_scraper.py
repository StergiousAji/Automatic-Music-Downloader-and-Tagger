import spotipy
import spotipy.util as util

import pytubefix as pytube
# import pytube
from ytmusicapi import YTMusic

from config import setup_spotify, username


RESET = "\u001b[0m"
GREEN = "\u001b[32m"
YELLOW = "\u001b[33m"
RED = "\u001b[31m"
MAGENTA = "\u001b[95m"
BLUE = "\u001b[36m"

# Config includes Spotify credential information
setup_spotify()

scope = "user-read-playback-state user-modify-playback-state user-read-currently-playing playlist-read-private playlist-modify-private streaming"
spotify = spotipy.Spotify(auth=util.prompt_for_user_token(username, scope))

def find_playlist(playlist_name):
    playlists = spotify.current_user_playlists()
    while playlists:
        for playlist in playlists['items']:
            if playlist and playlist['name'] == playlist_name:
                return spotify.playlist_items(playlist_id=playlist['uri'])

def seconds_to_time(seconds):
    return f"{int(seconds // 60)}:{(seconds % 60):05.2f}"

def time_to_seconds(time):
    time_split = time.split(':')
    return int(time_split[0])*60 + float(time_split[1])

def scrape_song_info(playlist):
    songs = []
    for i, song in enumerate(playlist['items']):
        artist = song['track']['album']['artists'][0]['name']
        track = song['track']['name']
        duration = int(song['track']['duration_ms']) / 1000.0
        explicit = song['track']['explicit']
        songs.append({"artist": artist, "track": track, "name": f"{artist} {track}", "duration": duration, "expliit": explicit})
        print(f"{i+1}. {artist} - {track}{' [E]' if explicit else ''} ({seconds_to_time(duration)})")
    
    return songs

def write_url(url):
    with open("urls.txt", 'a') as urls_file:
        urls_file.write(f"{url}\n")

def search_ytmusic(songs):
    ytmusic = YTMusic()
    yt_header = "https://www.youtube.com/watch?v="
    url_list = []
    for song in songs:
        search_results = ytmusic.search(f"{song['name']}")
        print(f"{YELLOW}{song['artist']} - {song['track']}:{RESET}")
        for result in search_results:
            watch_url = yt_header + result['videoId']
            explicit_match = song['explicit'] == result['isExplicit'] if 'isExplicit' in result else True
            print(f"Searching {GREEN}{watch_url}{RESET}")
            if song['track'] == result['title'] and abs(result['duration_seconds'] - song['duration']) < 0.5 and explicit_match:
                url_list.append(watch_url)
                write_url(watch_url)
                print()
                break
    
    return url_list

# [DEPRECATED]
def search_youtube(songs):
    url_list = []
    for song in songs:
        search = pytube.Search(f"{song['name']} audio")
        # print(f"\u001b[33m{song['artist']} - {song['track']}:\u001b[0m")
        print(f"{YELLOW}{song['artist']} - {song['track']}:{RESET}")
        for video in search.results:
            # print(f"Searching \u001b[32m{video.watch_url}\u001b[0m")
            print(f"Searching {GREEN}{video.watch_url}{RESET}")
            if abs(video.length - song['duration']) < 3.5:
            # if abs(time_to_seconds(video.len) - song['duration']) < 3.5:
                url_list.append(video.watch_url)
                write_url(video.watch_url)
                print()
                break
    
    return url_list