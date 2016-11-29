import sys
import os
import re
import argparse
from urllib.parse import urlparse
from enum import Enum
from pprint import pprint

import spotipy
import spotipy.util as util

import praw

class LinkType(Enum):
    unknown = 1
    artist = 2
    album = 3
    track = 4


def get_token(username):
    return util.prompt_for_user_token(username, "playlist-modify-public")


def retrieve_playlist(sp, user_id, playlist_id):
    all_tracks = []

    results = sp.user_playlist(user_id, playlist_id, fields="tracks,next")
    tracks = results["tracks"]

    all_tracks += [t["track"]["id"] for t in tracks["items"]]

    while "next" in tracks.keys():
        tracks = sp.next(tracks)
        if tracks is None:
            break

        all_tracks += [t["track"]["id"] for t in tracks["items"]]

    return all_tracks


def retrieve_posts(re, subreddit):
    posts = re.subreddit(subreddit).hot(limit=5)
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


def update_playlist(subreddit, re_username, re_client_id, re_client_secret, sp_username, sp_token, sp_playlist_id):
    sp = spotipy.Spotify(auth=sp_token)
    re = praw.Reddit(user_agent="web:ch.laurinbrandner.spotit:0.0.1 (by /u/" + re_username + ")", client_id=re_client_id, client_secret=re_client_secret)

    playlist = retrieve_playlist(sp, sp_username, sp_playlist_id)

    last_added_song = None
    new_tracks = []

    for post in retrieve_posts(re, subreddit):
        post_type = post_link_type(post)
        old_track_len = len(new_tracks)

        if post_type == LinkType.artist:
            artist_tracks = sp.artist_top_tracks(post.url)
            if len(artist_tracks) > 0:
                new_tracks.append(artist.tracks["tracks"][0]["id"])

        elif post_type == LinkType.album:
            album_tracks = [t["id"] for t in sp.album_tracks(post.url)["items"]]
            album_tracks = sorted(sp.tracks(album_tracks)["tracks"], key=lambda track: track["popularity"])
            if len(album_tracks) > 0:
                new_tracks.append(album_tracks[0]["id"])

        elif post_type == LinkType.track:
            new_tracks.append(post.url)

        if old_track_len == len(new_tracks):
            info = get_track_info(post.title)
            if info is not None:
                query = "artist:" + info[0] + " " + "track:" + info[1]
                results = sp.search(q=query, type="track")["tracks"]["items"]
                if len(results) > 0:
                    new_tracks.append(results[0]["id"])

    new_tracks = [t for t in new_tracks if t not in playlist]

    if len(new_tracks) > 0:
        sp.user_playlist_add_tracks(sp_username, sp_playlist_id, new_tracks)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Digest music subreddits")
    parser.add_argument("-r", help="the name of the subreddit")
    parser.add_argument("-su", help="the spotify username")
    parser.add_argument("-ru", help="the reddit username")

    args = parser.parse_args()

    subreddit = args.r
    sp_username = args.su
    re_username = args.ru

    token = get_token(sp_username)
    if not token:
        print("Can't get token for " + username)
        sys.exit()

    update_playlist(subreddit, sp_username, re_username, token, "alltracks.p")
