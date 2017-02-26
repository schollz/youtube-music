#!/usr/bin/python3
import sys
from lxml import html
import requests
import os
import urllib
import requests
import json
import multiprocessing
import random
import uuid

programSuffix = ""

def getURL(searchString):
    urlToGet = "https://www.youtube.com/results?search_query=" + urllib.parse.quote_plus(searchString)
    print("Getting %s" % urlToGet)
    page = requests.get(urlToGet)
    tree = html.fromstring(page.content)
    videos = tree.xpath('//h3[@class="yt-lockup-title "]')
    for video in videos:
        videoData = video.xpath('./a[contains(@href, "/watch")]')
        if len(videoData) == 0:
            continue
        if 'title' not in videoData[0].attrib or 'href' not in videoData[0].attrib:
            continue
        title = videoData[0].attrib['title']
        url = "https://www.youtube.com" + videoData[0].attrib['href']
        if 'googleads' in url:
            continue
        print("Found url '%s'" % url)
        try:
            timeText = video.xpath(
                './span[@class="accessible-description"]/text()')[0]
            minutes = int(timeText.split(':')[1].strip())
        except:
            pass
        if 'doubleclick' in title or 'list=' in url or 'album review' in title.lower():
            continue
        print("'%s' = '%s' @ %s " % (searchString, title, url))
        return url
    return ""


if __name__ == '__main__':
    is_windows = sys.platform.startswith('win')
    if is_windows:
        programSuffix = ".exe"

    if len(sys.argv) == 1:
        print("""
To get text:

    $ ./gettext.py "Barack Obama commencement speech"
""")
        sys.exit(1)


    try:
        os.mkdir("text")
    except:
        pass
    os.chdir("text")
    tempName = str(uuid.uuid4())
    text = sys.argv[1].strip()
    os.system("youtube-dl%s -o %s --write-sub --skip-download %s" %
              (programSuffix, tempName, getURL(text)))
    fulltext = ""
    with open(tempName+".en.vtt","r") as f:
        for line in f:
            if "WEBVTT" in line or len(line)==0 or "Kind:" in line or "Language:" in line or "-->" in line:
                continue
            fulltext += line.strip() + " "
    fulltext = fulltext.strip()
    print(fulltext)
    os.remove(tempName+".en.vtt")
