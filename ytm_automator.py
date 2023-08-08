from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from music_downloader_tagger import clean_folder
from music_downloader_tagger import recognise_song
from music_downloader_tagger import modify_file
from music_downloader_tagger import url_list
import os

chromeOptions = webdriver.ChromeOptions()
prefs = {"download.default_directory" : "C:\\Users\\jovin\\Documents\\Automatic-Music-Downloader-and-Tagger\\downloads"}
chromeOptions.add_experimental_option("prefs",prefs)
chromeOptions.add_argument('headless')

download_urls = []

def scrape_urls():
    print("Getting Download Links")
    
    with open("download_urls.txt", "w") as file:
        driver = webdriver.Chrome(options=chromeOptions)
        for url in url_list:
            # Navigate to website and search URL
            driver.get("https://youtubetomp3song.com/")
            urlInput = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "videoURL")))
            urlInput.send_keys(url)
            time.sleep(1)
            urlInput.send_keys(Keys.ENTER)

            # Click 'Download MP3' button
            time.sleep(1)
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, "download-mp3")))
            download_mp3 = driver.find_element(By.CLASS_NAME, "download-mp3")
            driver.execute_script("arguments[0].click();", download_mp3)
            time.sleep(1)

            try:
                download_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, "q192")))
                download_url = download_button.get_attribute('href')
                file.write(download_url + "\n")
            except Exception:
                file.write(" \n")
                print(f"\u001b[31m{url}\u001b[0m")
                continue
            
            download_urls.append(download_url)

    return download_urls

def download_mp3(urls=[]):
    print("Downloading...")
    if urls == []:
        with open("mp3_urls.txt", "r") as file:
            for url in file.readlines():
                driver = webdriver.Chrome(options=chromeOptions)
                driver.get(url)
                time.sleep(15)
                download_urls.append(url)

                # Modify most recently created audio file
                audio_file_path = f"downloads\\{max([f for f in os.scandir('downloads')], key=lambda x: x.stat().st_mtime).name}"
                print(audio_file_path)
                metadata = recognise_song(audio_file_path)
                if metadata:
                    print(f"Modifying \u001b[36m{metadata['artist']} - {metadata['title']}\u001b[0m")
                    modify_file(audio_file_path, metadata)
                else:
                    print("Nope, Skipped!\u001b[0m")


scrape_urls()
download_mp3()