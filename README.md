# Automatic Music Downloader and Tagger
Automatically downloads audio from a list of URLs and fills in the relevant MP3 tags (including cover art).

\
Program can either be run by itself to input URLs one by one:
```shell
> python music_downloader_tagger.py
```

or by passing a text file containing a list of URLs on separate lines:
```shell
> python music_downloader_tagger.py -f [filename?]
```

or by using a Spotify playlist:
```shell
> python music_downloader_tagger.py -s [playlist?]
```

The `downloads` folder can be cleared with the `-c` flag as well as optionally clearing the passed in file:
```shell
> python music_downloader_tagger.py -c [filename?]
```