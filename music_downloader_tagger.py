import pytube, subprocess
import os, shutil, argparse
from ShazamAPI import Shazam
import urllib
import music_tag
import requests
import subprocess

import youtube_dl

from ytm_automator import scrape_urls, download_mp3

from spotify_yt_scraper import find_playlist, scrape_song_info, search_youtube

def clean_folder(filename):
    if "downloads" in os.listdir():
        print("\u001b[32mCleaning downloads...\u001b[0m")
        shutil.rmtree("downloads")
        os.mkdir("downloads")
        open("downloads/.placeholder", 'w').close()
        subprocess.check_call(["attrib","+H","downloads/.placeholder"])
    
    if not filename.isspace():
        print(f"\u001b[32mCleaning {filename}...\u001b[0m")
        open(f"{filename}", 'w').close()

def download_audio(url):
    default_file = os.path.join("downloads", "Video Not Available.mp4")
    out_file = default_file
    while os.path.relpath(out_file) == default_file:
        if os.path.exists(out_file):
            os.remove(out_file)
        ydl = pytube.YouTube(url, use_oauth=True, allow_oauth_cache=True)
        out_file = ydl.streams.get_audio_only().download("downloads")

    audio_file = f"{out_file.split('.')[0]}.mp3"
    print(f"Downloading \u001b[95m{os.path.basename(audio_file)}\u001b[0m")
    subprocess.run(['ffmpeg', '-i', out_file, '-b:a', '192K', audio_file, '-hide_banner', '-loglevel', 'quiet'])
    os.remove(out_file)
    return audio_file

def download_audio_YDL(url):
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

def recognise_song(file_path):
    metadata = {}
    with open(file_path, 'rb') as mp3_file:
        shazam = Shazam(mp3_file.read())
        recognised = next(shazam.recognizeSong())[1]
        
        if "track" not in recognised:
            return

        recognised = recognised["track"]
        metadata['title'] = urllib.parse.unquote_plus(recognised["urlparams"]["{tracktitle}"])
        metadata['artist'] = urllib.parse.unquote_plus(recognised["urlparams"]["{trackartist}"])
        if "images" in recognised:
            metadata['imageURL'] = recognised["images"]["coverart"]
    
    return metadata

illegal_chars = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
def validate_filename(filename):
    for c in filename:
        if c in illegal_chars:
            filename = filename.replace(c, ";")
    return filename

def modify_file(file_path, metadata):
    new_filename = validate_filename(f"{metadata['artist']} - {metadata['title']}")
    new_filename = os.path.join("downloads", new_filename)

    if not os.path.exists(new_filename):
        os.rename(file_path, f"{new_filename}.mp3")
        song = music_tag.load_file(f"{new_filename}.mp3")
        song['tracktitle'] = metadata['title']
        song['artist'] = metadata['artist']
        song['albumartist'] = metadata['artist']
        if "imageURL" in metadata:
            song['artwork'] = requests.get(metadata['imageURL']).content

        song.save()
    else:
        print(f"\u001b[31mFile '{new_filename}' already exists! Skipped\u001b[0m")


parser = argparse.ArgumentParser(description="Program to download and tag mp3 audio files.")
parser.add_argument("-c", "--clean", help="Option to clean downloads folder and passed urls file", nargs='?', type=str, const=" ")
parser.add_argument("-f", "--file", help="Pass in text file of URLs (defaults to urls.txt)", nargs='?', type=str, const="urls.txt")
parser.add_argument("-y", "--ytm", help="Use YouTubeToMP3 to download songs", action="store_true")
parser.add_argument("-s", "--spotify", help="Scrape songs from Spotify", nargs='?', type=str, const="new-songs")

args = parser.parse_args()

if __name__ == "__main__":
    url_list = []

    if (args.clean):
        clean_folder(args.clean)

    # Read urls.txt by default
    if (args.file):
        with open(args.file) as urls_file:
            print("\u001b[33mReading URLs...\u001b[0m")
            for line in urls_file.readlines():
                url = line.replace("\n", "")
                print(f"\t{url}")
                if url.startswith("https://"):
                    url_list.append(url)
    
    if (args.spotify):
        pl_new_songs = find_playlist(args.spotify)
        songs = scrape_song_info(pl_new_songs)
        print()
        url_list.extend(search_youtube(songs))
    else:
        while True:
            url = input("Enter a URL: ")
            if url == "":
                break
            if url.startswith("https://"):
                url_list.append(url)
            else:
                print("\u001b[31mInvalid URL submitted!\u001b[0m")
        
    # Download and modify metadata
    print()
    if (args.ytm):
        scrape_urls(url_list)
        download_mp3()
    else:
        for url in url_list:
            download_audio(url)

    print()
    # Modify unmodified downloads in order of modified time
    downloads = sorted([os.path.join("downloads", x) for x in os.listdir("downloads") if x.endswith(".mp3") or x.endswith(".m4a")], key=lambda x: os.path.getmtime(x))
    for audio_file_path in downloads:
        song = music_tag.load_file(audio_file_path)
        if not song["tracktitle"]:
            metadata = recognise_song(audio_file_path)
            if metadata:
                print(f"Modifying \u001b[36m{metadata['artist']} - {metadata['title']}\u001b[0m")
                modify_file(audio_file_path, metadata)
            else:
                print(f"Skipping \u001b[31m{os.path.basename(audio_file_path)}\u001b[0m")