#!/usr/bin/env python
import argparse
import random
import time
import urllib.request as RE
import xml.etree.ElementTree as ET

class Track(object):

    def __init__(self, name, artist, album):
        self.name = name
        self.artist = artist
        self.album = album

    @classmethod
    def fromstring(cls, xml):
        root = ET.fromstring(xml)
        name = root.find(tag('name')).text
        artist = root.find(tag('artist')).find(tag('name')).text
        album = root.find(tag('album')).find(tag('name')).text
        return cls(name, artist, album)

    def __str__(self):
        return ' '.join([self.name, self.artist, self.album])

class Album(object):

    def __init__(self, name, artist):
        self.name = name
        self.artist = artist

    def __str__(self):
        return ' '.join([self.name, self.artist])

    def __eq__(self, other):
        return self.name == other.name and self.artist == other.artist

    def __hash__(self):
        return hash(self.name + self.artist)

class Playlist(object):

    def __init__(self, tracks):
        self.tracks = tracks

    @classmethod
    def fromfile(cls, filename):
        with open(filename) as f:
            ids = track_ids(f.read().split())
            track_list = [ Track.fromstring(download_meta_data(spotify_uri(i))) for i in ids ]
            return Playlist(track_list)

    def albums(self):
        a = set()
        for t in self.tracks:
            a.add(Album(t.album, t.artist))
        return a

def track_ids(track_urls):
    spotify_url = 'http://open.spotify.com/track/'
    for s in track_urls:
        if s.startswith(spotify_url):
            yield s.replace(spotify_url, '')

def spotify_uri(track):
    return 'spotify:track:' + track

def download_meta_data(uri, tries = 3):
    for turn in range(1, tries):
        try:
            response = RE.urlopen('http://ws.spotify.com/lookup/1/?uri=' + uri)
            return response.read()
        except:
            time.sleep(random.randint(1, 3))
    return None

def tag(name):
    return '{http://www.spotify.com/ns/music/1}' + name

def main():
    parser = argparse.ArgumentParser(prog = 'spex')
    parser.add_argument('action')
    parser.add_argument('playlist')
    args = parser.parse_args()

    if args.action == 'tracks':
        for a in Playlist.fromfile(args.playlist).tracks:
            print(a)
    elif args.action == 'albums':
        for a in Playlist.fromfile(args.playlist).albums():
            print(a)
    else:
        print('Unkown action: \'' + args.action + '\'')

if __name__ == "__main__":
    main()
