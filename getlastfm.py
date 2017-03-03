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

programSuffix = ""


def downloadURL(url):
    if len(url) == 0:
        return
    os.system("youtube-dl%s -x --audio-quality 3 --audio-format mp3 %s" %
              (programSuffix, url))

def getYoutubeAndRelatedLastFMTracks(lastfmURL):
    print('Working on %s' % lastfmURL)
    youtubeURL = ""
    lastfmTracks = []

    r = requests.get(lastfmURL)
    tree = html.fromstring(r.content)
    youtubeSection = tree.xpath('//div[@class="video-preview"]')
    if len(youtubeSection) > 0:
        possibleYoutubes = youtubeSection[0].xpath('//a[@target="_blank"]')
        for possibleYoutube in possibleYoutubes:
            if 'href' in possibleYoutube.attrib:
                if 'youtube.com' in possibleYoutube.attrib['href']:
                    youtubeURL = possibleYoutube.attrib['href']
                    break


    sections = tree.xpath('//section[@class="grid-items-section"]')
    for track in sections[0].findall('.//a'):
        lastfmTracks.append('https://www.last.fm' + track.attrib['href'])

    lastfmTracks = list(set(lastfmTracks))
    return (youtubeURL,lastfmTracks)

def getTracks(searchTrack):
    r = requests.get('https://www.last.fm/search?q=%s' % searchTrack.replace(' ','+'))
    tree = html.fromstring(r.content)
    possibleTracks = tree.xpath('//span/a[@class="link-block-target"]')
    firstURL = ""
    for i,track in enumerate(possibleTracks):
        firstURL = 'https://www.last.fm' + track.attrib['href']
        break
    print(firstURL)

    youtubeLinks = []
    data = getYoutubeAndRelatedLastFMTracks(firstURL)
    finishedLastFMTracks = [firstURL]
    youtubeLinks.append(data[0])
    lastfmTracksNext = data[1]

    for i in range(2):
        lastfmTracks = list(set(lastfmTracksNext)-set(finishedLastFMTracks))
        p = multiprocessing.Pool(multiprocessing.cpu_count())
        lastfmTracksNext = []
        for data in p.map(getYoutubeAndRelatedLastFMTracks, lastfmTracks):
            youtubeLinks.append(data[0])
            lastfmTracksNext += data[1]
        finishedLastFMTracks += lastfmTracks

    print(youtubeLinks)
    newDir = '-'.join(searchTrack.split())
    print("Saving tracks to %s" % newDir)
    try:
        os.mkdir(newDir)
    except:
        pass
    os.chdir(newDir)
    p = multiprocessing.Pool(multiprocessing.cpu_count())
    p.map(downloadURL, youtubeLinks)

if __name__ == '__main__':
    is_windows = sys.platform.startswith('win')
    if is_windows:
        programSuffix = ".exe"

    try:
        searchTrack = sys.argv[1]
        getTracks(searchTrack)
    except:
        print("Usage: ./getlastfm.py 'the beatles hey jude'")
        print("Make sure ffmpeg and youtube-dl are installed")
        sys.exit(-1)
    


    


