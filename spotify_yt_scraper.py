import spotipy
import spotipy.util as util
import os

from selenium import webdriver
from selenium.webdriver.common.by import By

import pytube

os.environ["SPOTIPY_CLIENT_ID"] = "24636ac803284e34931524e761ce9019"
os.environ["SPOTIPY_CLIENT_SECRET"] = "d23cb9a2f3fb407d80863201b848ea4f"
os.environ["SPOTIPY_REDIRECT_URI"] = "https://localhost:8888/callback"

scope = "user-read-playback-state user-modify-playback-state user-read-currently-playing playlist-read-private playlist-modify-private streaming"
username = "gamer33361"
spotify = spotipy.Spotify(auth=util.prompt_for_user_token(username, scope))

def find_playlist(playlist_name):
    playlists = spotify.current_user_playlists()
    while playlists:
        for playlist in playlists['items']:
            if playlist['name'] == playlist_name:
                return spotify.playlist_items(playlist_id=playlist['uri'])

def seconds_to_time(seconds):
    return f"{int(seconds // 60)}:{seconds % 60}"

def time_to_seconds(time):
    time_split = time.split(':')
    return int(time_split[0])*60 + float(time_split[1])

def scrape_song_info(playlist):
    songs = []
    for i, song in enumerate(playlist['items']):
        artist = song['track']['album']['artists'][0]['name']
        track = song['track']['name']
        duration = int(song['track']['duration_ms']) / 1000
        songs.append({"name": f"{artist} {track}", "duration": duration})
        print(f"{i+1}. {songs[i]['name']} ({seconds_to_time(duration)}))")
    
    return songs


chromeOptions = webdriver.ChromeOptions()
chromeOptions.add_argument('headless')

# def write_url(url):
#     with open("urls.txt", 'a') as urls_file:
#         urls_file.write(f"{url}\n")

def search_youtube(songs):
    url_list = []
    for song in songs:
        # driver.get(f"https://www.youtube.com/results?search_query={'+'.join(song['name'].split(' '))}+audio")
        # WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='Reject the use of cookies and other data for the purposes described']"))).click()
        # time.sleep(1000)

        search = pytube.Search(f"{song['name']} audio")
        for video in search.results:
            driver = webdriver.Chrome(options=chromeOptions)
            driver.get(video.watch_url)
            duration = driver.find_element(By.CLASS_NAME, "ytp-time-duration")
            
            if abs(time_to_seconds(duration.text) - song['duration']) < 5:
                url_list.append(video.watch_url)
                break
    
    return url_list