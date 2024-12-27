# TODO:
#   - Support Release Date


import requests
import cloudscraper
from bs4 import BeautifulSoup
import json
import os
import eyed3
import json
from eyed3.id3.frames import ImageFrame

downloadDir = os.path.expanduser("~/Music/STACKS")
saveCoverInId3 = False

def main():
    albumURL = input("Enter Bandcamp album URL: ")

    scraper = cloudscraper.create_scraper()
    response = scraper.get(albumURL)
    soup = BeautifulSoup(response.content, "html.parser")

    # parse album info from html
    JSONString = soup.head.find("script", {"data-tralbum": True})["data-tralbum"]
    JSON = json.loads(JSONString)

    albumTitle = JSON["current"]["title"]
    albumArtist = JSON["artist"]

    # parse cover art url from html and download
    coverArtUrl = soup.find(id="tralbumArt").a["href"]
    coverArtResponse = requests.get(coverArtUrl)
    coverArtData = coverArtResponse.content

    # Create directory for artist and album
    albumDir = f"{downloadDir}/{albumArtist}/{albumTitle}"
    os.makedirs(albumDir, exist_ok=True)

    print(f"Downloading Album: {albumTitle} by {albumArtist}")

    with open(f"{albumDir}/info.json", "w") as file:
        json.dump(JSON, file)

    with open(f"{albumDir}/cover.jpg", "wb") as file:
        file.write(coverArtData)

    trackInfoList = JSON["trackinfo"]
    for trackInfo in trackInfoList:
        url = trackInfo["file"]["mp3-128"]
        title = trackInfo["title"]
        trackNum = trackInfo["track_num"]

        print(f"Downloading: {url}")
        mp3Response = requests.get(url)
        mp3Path = f"{albumDir}/{trackNum}. {title}.mp3"
        print(f"Writing file to: {mp3Path}")
        with open(mp3Path, "wb") as file:
            file.write(mp3Response.content)

        addID3Tags(mp3Path, title, albumArtist, albumTitle, albumArtist, trackNum, coverArtData)

def addID3Tags(mp3Path, title, artist, album, albumArtist, trackNum, coverArtData):
    print(mp3Path)
    file = eyed3.load(mp3Path)
    if file.tag == None:
        file.initTag()
    file.tag.title = title
    file.tag.artist = artist
    file.tag.album = album
    file.tag.album_artist = albumArtist
    file.tag.track_num = int(trackNum)
    if saveCoverInId3:
        file.tag.images.set(ImageFrame.FRONT_COVER, coverArtData, "image/jpeg")
    
    file.tag.save()

main()