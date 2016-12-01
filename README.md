# spotit

[![Playlist: r/electronicmusic](https://img.shields.io/badge/playlist-r/electronicmusic-blue.svg?style=flat&colorB=1DB955)](https://open.spotify.com/user/lbrndnr/playlist/7oLEnqkhkj0UwArKGsx1H4)
[![Twitter: @lbrndnr](https://img.shields.io/badge/contact-@lbrndnr-blue.svg?style=flat)](https://twitter.com/lbrndnr)
[![License](http://img.shields.io/badge/license-MIT-green.svg?style=flat)](https://github.com/lbrndnr/ImagePickerSheetController/blob/master/LICENSE)

## About
This is a little experiment. It's a python script that parses a given subreddit and saves the music posts it finds to a playlist on Spotify.

This makes it easy to setup a server which does that on a regular basis. I've done so to parse [r/electronicmusic](https://www.reddit.com/r/electronicmusic/). You can follow that [playlist](https://open.spotify.com/user/lbrndnr/playlist/7oLEnqkhkj0UwArKGsx1H4) too of course.

## Usage
In order to create your own playlist, it's easiest if you write a secondary script that imports spotit and passes it all the paramter it needs. Here's an example:
```python
import os
import spotipy.oauth2 as oauth2
import spotit

sp_client_id = [YOUR_CLIENT_ID]
sp_client_secret = [YOUR_CLIENT_SECRET]
sp_redirect_uri = [YOUR_REDIRECT_URI]

re_client_id = [YOUR_CLIENT_ID]
re_client_secret = [YOUR_CLIENT_SECRET]

path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "access_token")

credentials = oauth2.SpotifyOAuth(sp_client_id, sp_client_secret, sp_redirect_uri, scope="playlist-modify-public", cache_path=path)
token_info = credentials.get_cached_token()
token = token_info["access_token"]

spotit.update_playlist([NAME_OF_YOUR_PLAYLIST], [REDDIT_USERNAME], re_client_id, re_client_secret, [SPOTIFY_USERNAME], token, [PLAYLIST_ID])
```

## Requirements
spotit requires `spotipy` and `praw`

## Author
I'm Laurin Brandner, I'm on [Twitter](https://twitter.com/lbrndnr).

## License
spotit is licensed under the [MIT License](http://opensource.org/licenses/mit-license.php).
