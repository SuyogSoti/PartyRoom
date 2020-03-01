import spotipy
from typing import List, Optional, Dict, Any
import flask_helpers as flsk_help
from spotipy.oauth2 import SpotifyOAuth
import os
import datetime

SPOTIPY_REDIRECT_URI = 'http://localhost:5000/callback/spotify'
PORT_NUMBER = 3000
SCOPE = 'user-library-read user-top-read'
CACHE = '.spotipyoauthcache'

sp_oauth = SpotifyOAuth(os.environ.get("SPOTIPY_CLIENT_ID"),
                        os.environ.get("SPOTIPY_CLIENT_SECRET"),
                        SPOTIPY_REDIRECT_URI,
                        scope=SCOPE,
                        cache_path=CACHE)


def getSPOauthURI():
    auth_url = sp_oauth.get_authorize_url()
    return auth_url


def get_user_from_access_token(token: Optional[str]) -> Optional[Dict[str, Any]]:
    if token:
        spotify = spotipy.Spotify(token)
        return spotify.current_user()


def refresh_token_if_necessary(users: List[flsk_help.User], db: flsk_help.SQLAlchemy):
    """
    Refreshes the token of the users given and updates the db with the new refresh token
    """
    for user in users:
        if user and user.token_expiration_time <= datetime.datetime.now():
            token_info = sp_oauth.refresh_access_token(user.refresh_token)
            user.access_token = token_info["access_token"]
            user.refresh_token = token_info["refresh_token"]
    db.session.commit()
