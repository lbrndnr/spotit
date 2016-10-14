import sys
import os
import re
from urllib.parse import urlparse
from enum import Enum
from pprint import pprint

import spotipy
import spotipy.util as util

import praw

sp_username = "lbrndnr"

reddit = praw.Reddit(user_agent="web:ch.lbrndnr.rmusic:0.0.1 (by /u/" + REDDIT_USERNAME + ")")

class LinkType(Enum):
    unknown = 1
    artist = 2
    album = 3
    track = 4


def getToken():
    return util.prompt_for_user_token(sp_username, "playlist-modify-public")


def retrieve_playlist(sp, user_id, playlist_name):
    offset = 0
    total = 1
    while offset < total:
        response = sp.user_playlists(user_id, offset=offset)
        playlists = response["items"]
        playlist = [p for p in playlists if p["name"] == playlist_name]
        if playlist:
            return playlist[0]

        offset += len(playlists)
        total = response["total"]


def retrieve_posts():
    subreddit = reddit.get_subreddit("electronicmusic")
    posts = subreddit.get_hot()
    songs = [p for p in posts if not p.is_self and p.media is not None]

    return songs


def post_link_type(post):
    o = urlparse(post.url)
    if "spotify" in o.netloc:
        if "artist" in o.path:
            return LinkType.artist
        elif "album" in o.path:
            return LinkType.album
        elif "track" in o.path:
            return LinkType.track

    return LinkType.unknown


def get_track_info(name):
    delimiters = [("(", ")"), ("[", "]")]
    for left, right in delimiters:
        while True:
            start = name.find(left)
            end = name.find(right)
            if start == -1 or end == -1:
                break
            else:
                name = name[:start] + name[end+1:]

    if "--" in name:
        info = name.split("--") 
    else:
        info = name.split("-")

    if len(info) > 1:
        return (info[0].strip(), info[1].strip())


if __name__ == "__main__":
    token = getToken()
    if not token:
        print("Can't get token for " + username)
        sys.exit()

    sp = spotipy.Spotify(auth=token)

    playlist = retrieve_playlist(sp, sp_username, "r/electronicmusic")
    saved_tracks = sp.user_playlist_tracks(sp_username, playlist["id"])

    last_added_song = None
    tracks = []

    for post in retrieve_posts():
        post_type = post_link_type(post)

        if post_type == LinkType.artist:
            print("ITs an artist")
        elif post_type == LinkType.album:
            pprint(dir(sp.album_tracks(post.url)))
        elif post_type == LinkType.track:
            print("ITs a track")
        else:
            info = get_track_info(post.title)
            if info is not None:
                query = "artist:" + info[0] + " " + "track:" + info[1]
                results = sp.search(q=query, type="track")["tracks"]["items"]
                if len(results) > 0:
                    tracks.append(results[0]["id"])

    if len(tracks) > 0:
        sp.user_playlist_add_tracks(sp_username, playlist["id"], tracks)
