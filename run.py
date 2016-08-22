import sys
from lxml import html
import requests
import os
import urllib
import requests
import json
import multiprocessing


def spotify(user,playlist,oauth):
    url = 'https://api.spotify.com/v1/users/'+user+'/playlists/'+playlist+'/tracks'
    headers = {'Authorization':'Bearer ' + oauth}
    r = requests.get(url,headers=headers)
    a = r.json()
    trackList = []
    for item in a['items']:
        trackList.append(item['track']['artists'][0]['name'] + " - " + item['track']['album']['name'] + " - " + item['track']['name'])
    return trackList


def getURL(searchString):
    page = requests.get("https://www.youtube.com/results?search_query=" + urllib.parse.quote_plus(searchString))
    tree = html.fromstring(page.content)
    videos = tree.xpath('//a[contains(@href, "/watch")]')
    for video in videos:
        if 'title' in video.attrib and 'href' in video.attrib:
            if 'doubleclick' in video.attrib['href']:
                continue
            print(video.attrib['title'])
            return "https://www.youtube.com"+ video.attrib['href']
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
        trackList = spotify(sys.argv[1],sys.argv[2],sys.argv[3])
        directory = sys.argv[2]
    elif len(sys.argv)==1:
        print("""
USAGE:
    To download a single track: 
        python3 run.py "Led Zepplin - Stairway to Heaven"

    To download a txt-file playlist:
        python3 run.py Zepplin.txt

Make a file, Zepplin.txt with all the files.

    To download a Spotify playlist:
        python3 run.py USER PLAYLIST OAUTH

First go into Spotify, to your playlist and copy the USER ID and the PLAYLIST ID.
To get the OAUTH, goto 
https://developer.spotify.com/web-api/console/get-playlist-tracks/#complete
Get an OAUTH token and click "TRY IT". Then copy all the stuff after "Bearer "
""")
        sys.exit(1)
    elif '.txt' in sys.argv[1]:
        directory = sys.argv[1].split(".txt")[0]
        with open(sys.argv[1],'r') as f:
            for line in f:
                trackList.append(line.strip())
    elif len(sys.argv)==2:
        trackList.append(sys.argv[1])
    else:
        print("?")
        sys.exit(1)

    for track in trackList:
        urls.append(getURL(track))
    try:
        os.mkdir(directory)
    except:
        pass
    os.chdir(directory)
    p = multiprocessing.Pool(multiprocessing.cpu_count())
    p.map(downloadURL,urls)
    print("%d songs downloaded to %s." % (len(urls),directory))
