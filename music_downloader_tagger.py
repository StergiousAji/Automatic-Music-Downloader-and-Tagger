import pytube, subprocess
import os, shutil, sys
from ShazamAPI import Shazam
import urllib
import music_tag
import requests

def clean_folder():
    if "downloads" in os.listdir():
        shutil.rmtree("downloads")
        os.mkdir("downloads")

def download_audio(url):
    ydl = pytube.YouTube(url)
    out_file = ydl.streams.get_audio_only().download("downloads")
    audio_file = f"downloads\\{ydl.title}.mp3"
    subprocess.run(['ffmpeg', '-i', out_file, '-b:a', '192K', audio_file, '-hide_banner', '-loglevel', 'quiet'])
    os.remove(out_file)
    return audio_file

def recognise_song(file_path):
    metadata = {}
    with open(file_path, 'rb') as mp3_file:
        shazam = next(Shazam(mp3_file.read()).recognizeSong())[1]
        if "track" in shazam:
            recognised = shazam["track"]
        else:
            print(f"ERROR\n{shazam}")
            return
        
        metadata['title'] = urllib.parse.unquote_plus(recognised["urlparams"]["{tracktitle}"])
        metadata['artist'] = urllib.parse.unquote_plus(recognised["urlparams"]["{trackartist}"])
        metadata['imageURL'] = recognised["images"]["coverart"]
    
    return metadata

def modify_file(file_path, metadata):
    new_file_name = f"downloads\\{metadata['artist']} - {metadata['title']}"

    os.rename(file_path, f"{new_file_name}.mp3")
    song = music_tag.load_file(f"{new_file_name}.mp3")
    song['tracktitle'] = metadata['title']
    song['artist'] = metadata['artist']
    song['albumartist'] = metadata['artist']
    song['artwork'] = requests.get(metadata['imageURL']).content

    # with open(f"{new_file_name}.jpg", "wb") as image:
    #     image.write(requests.get(metadata['imageURL']).content)
    
    song.save()

url_list = []
clean_folder()
while True:
    url = input("Enter a URL: ")
    if url == "":
        break
    
    url_list.append(url)

print()
# Download and modify metadata
for url in url_list:
    audio_file_path = download_audio(url)
    metadata = recognise_song(audio_file_path)
    if metadata:
        print(f"Modifying \u001b[36m{metadata['artist']} - {metadata['title']}\u001b[0m")
        modify_file(audio_file_path, metadata)
    else:
        print("\u001b[31mNope, Skipped!\u001b[0m")