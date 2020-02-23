import spotipy
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth
import os

SPOTIPY_REDIRECT_URI = 'http://localhost:5000/callback/spotify'
PORT_NUMBER = 3000
SCOPE = 'user-library-read'
CACHE = '.spotipyoauthcache'


sp_oauth = SpotifyOAuth(os.environ.get("SPOTIPY_CLIENT_ID"),
                        os.environ.get("SPOTIPY_CLIENT_SECRET"),
                        SPOTIPY_REDIRECT_URI,
                        scope=SCOPE,
                        cache_path=CACHE)


def getSPOauthURI():
    auth_url = sp_oauth.get_authorize_url()
    return auth_url


sp = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())


def get_user_from_access_token(token):
    if token:
        spotify = spotipy.Spotify(token)
        return spotify.current_user()