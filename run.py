import sys
from lxml import html
import requests
import os
import urllib

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
    print(sys.argv[1])
    if '.txt' in sys.argv[1]:
        print("Got document...")
        with open(sys.argv[1],'r') as f:
            for line in f:
                print(line)
                downloadURL(getURL(line.strip()))
    else:
        downloadURL(getURL(sys.argv[1]))
    print("HI")

