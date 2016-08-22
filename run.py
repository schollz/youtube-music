import sys
from lxml import html
import requests
import os
import urllib
import requests
import json
import multiprocessing


def spotify(user, playlist, oauth):
    url = 'https://api.spotify.com/v1/users/' + \
        user + '/playlists/' + playlist + '/tracks'
    headers = {'Authorization': 'Bearer ' + oauth}
    r = requests.get(url, headers=headers)
    a = r.json()
    trackList = []
    for item in a['items']:
        trackList.append(item['track']['artists'][0][
                         'name'] + " - " + item['track']['album']['name'] + " - " + item['track']['name'])
    url = 'https://api.spotify.com/v1/users/' + user + '/playlists/' + playlist
    headers = {'Authorization': 'Bearer ' + oauth}
    r = requests.get(url, headers=headers)
    a = r.json()
    directory = a['name'] + ' - ' + a['id']
    return trackList, directory


def getURL(searchString):
    page = requests.get("https://www.youtube.com/results?search_query=" +
                        urllib.parse.quote_plus(searchString))
    tree = html.fromstring(page.content)
    videos = tree.xpath('//h3[@class="yt-lockup-title "]')
    for video in videos:
        title = video.xpath(
            './a[contains(@href, "/watch")]')[0].attrib['title']
        url = "https://www.youtube.com" + \
            video.xpath('./a[contains(@href, "/watch")]')[0].attrib['href']
        try:
            minutes = int(video.xpath(
                './span[@class="accessible-description"]/text()')[0].split(':')[1].strip())
            if minutes > 12:
                continue
        except:
            pass
        if 'doubleclick' in title or 'list=' in url or 'album review' in title.lower():
            continue
        print("'%s' = '%s' @ %s " % (searchString, title, url))
        return url
    return ""


def downloadURL(url):
    if len(url) == 0:
        return
    os.system("youtube-dl -x --audio-quality 2 --audio-format mp3 " + url)

if __name__ == '__main__':
    trackList = []
    urls = []
    directory = "default"
    if len(sys.argv) > 3:
        trackList, directory = spotify(sys.argv[1], sys.argv[2], sys.argv[3])
    elif len(sys.argv) == 1:
        print("""
To download a single track:

    $ python3 run.py "Led Zepplin - Stairway to Heaven"

To download a txt-file playlist:

    $ python3 run.py Zepplin.txt

    Make the file, 'Zepplin.txt' that contains a list of artist/track names.
    Songs will be stored in 'Zepplin' folder.


To download a Spotify playlist:

    $ python3 run.py USER-ID PLAYLIST-ID OAUTH

    Go into Spotify, find your playlist and copy the USER-ID and PLAYLIST-ID
    To get the OAUTH, goto
    https://developer.spotify.com/web-api/console/get-playlist-tracks/#complete
    Get an OAUTH token and click "TRY IT". Then copy all the stuff after "Bearer "

""")
        sys.exit(1)
    elif '.txt' in sys.argv[1]:
        directory = sys.argv[1].split(".txt")[0]
        with open(sys.argv[1], 'r') as f:
            for line in f:
                trackList.append(line.strip())
    elif len(sys.argv) == 2:
        trackList.append(sys.argv[1])
    else:
        print("?")
        sys.exit(1)

    print("Tracklist to use:")
    for track in trackList:
        print(track)
        urls.append(getURL(track))
    try:
        os.mkdir(directory)
    except:
        if directory == "default":
            pass
        else:
            print("Directory '%s' already exists, exiting." % directory)
            sys.exit(-1)
    os.chdir(directory)
    p = multiprocessing.Pool(multiprocessing.cpu_count())
    p.map(downloadURL, urls)
    print("%d songs downloaded to %s." % (len(urls), directory))
