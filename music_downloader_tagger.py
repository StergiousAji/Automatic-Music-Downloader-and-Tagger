import pytube, subprocess
import os, shutil, sys, argparse
from ShazamAPI import Shazam
import urllib
import music_tag
import requests

def clean_folder():
    if "downloads" in os.listdir():
        shutil.rmtree("downloads")
        os.mkdir("downloads")

def download_audio(url):
    default_file = "downloads\\Video Not Available.mp4"
    out_file = default_file
    while os.path.relpath(out_file) == default_file:
        if os.path.exists(out_file):
            os.remove(out_file)
        ydl = pytube.YouTube(url, use_oauth=True)
        out_file = ydl.streams.get_audio_only().download("downloads")

    audio_file = f"{out_file.split('.')[0]}.mp3"
    subprocess.run(['ffmpeg', '-i', out_file, '-b:a', '192K', audio_file, '-hide_banner', '-loglevel', 'quiet'])
    os.remove(out_file)
    return audio_file

def recognise_song(file_path):
    metadata = {}
    with open(file_path, 'rb') as mp3_file:
        shazam = Shazam(mp3_file.read())
        recognised = next(shazam.recognizeSong())[1]
        
        if "track" in recognised:
            recognised = recognised["track"]
        else:
            print(f"\u001b[31mERROR\n{recognised}")
            return
        
        metadata['title'] = urllib.parse.unquote_plus(recognised["urlparams"]["{tracktitle}"])
        metadata['artist'] = urllib.parse.unquote_plus(recognised["urlparams"]["{trackartist}"])
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
    new_filename = f"downloads\\{new_filename}"

    os.rename(file_path, f"{new_filename}.mp3")
    song = music_tag.load_file(f"{new_filename}.mp3")
    song['tracktitle'] = metadata['title']
    song['artist'] = metadata['artist']
    song['albumartist'] = metadata['artist']
    song['artwork'] = requests.get(metadata['imageURL']).content

    song.save()


parser = argparse.ArgumentParser(description="Program to download and tag mp3 audio files.")
parser.add_argument("-c", "--clean", help="Set clean downloads folder to True", action="store_true")
parser.add_argument("-f", "--file", help="Pass in text file of URLs", type=str)

args = parser.parse_args()

url_list = []

if (args.clean):
    print("Cleaning downloads...")
    clean_folder()

if (args.file):
    with open(args.file) as urls_file:
        print("Reading URLs...")
        for line in urls_file.readlines():
            url = line.replace("\n", "")
            print(f"\t{url}")
            url_list.append(url)
else:
    while True:
        url = input("Enter a URL: ")
        if url == "":
            break
        url_list.append(url)
        

# Download and modify metadata
# OPTIMISE!!
print()
for url in url_list:
    audio_file_path = download_audio(url)
    metadata = recognise_song(audio_file_path)
    if metadata:
        print(f"Modifying \u001b[36m{metadata['artist']} - {metadata['title']}\u001b[0m")
        modify_file(audio_file_path, metadata)
    else:
        print("Nope, Skipped!\u001b[0m")