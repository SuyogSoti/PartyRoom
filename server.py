from flask import render_template, request, redirect, session, jsonify
import json
import requests
from flask_helpers import app, db, Party, User
from party_form import PartyRoomCreateForm, PartyRoomJoinForm
from spotify import sp_oauth, getSPOauthURI, get_user_from_access_token, refresh_token_if_necessary
import spotipy
from config import Config
import datetime
import traceback

db.create_all()

MAX_CLIENTS_PER_ROOM = 100


@app.route('/party/<int:room_id>')
def party(room_id):
    user = get_current_user()
    if not user:
        return redirect("/")

    party = Party.query.get(int(room_id))
    if not party:
        return redirect("/")

    tracks = {}

    number_of_songs_to_store = MAX_CLIENTS_PER_ROOM
    songs_per_client = int(number_of_songs_to_store / len(party.clients))
    refresh_token_if_necessary(party.clients, db)
    for client in party.clients:
        spotify = spotipy.Spotify(client.access_token)
        try:
            user_tracks = spotify.current_user_top_tracks(
                limit=songs_per_client).get("items", [])
            for track in user_tracks:
                key = track.get("uri")
                if key not in tracks:
                    tracks[key] = [0, track]
                tracks[key][0] += 1 + (
                    party.danceability * track.get("danceability", 0)) + (
                        party.loudness * track.get("loudness", 0)) + (
                            party.energy * track.get("energy", 0)) + (
                                party.speechiness * track.get("speechiness", 0))

        except Exception as e:
            print(traceback.format_exc())

    if not tracks:
        return redirect("/")

    spotify = spotipy.Spotify(user.access_token)
    seeds = sorted(tracks,
                   key=lambda x:
                   (tracks[x][0], tracks[x][1].get("popularity")),
                   reverse=True)[:5]
    kwarg = {
        "target_danceability": party.danceability,
        "target_loudness": party.loudness,
        "target_energy": party.energy,
        "target_speechiness": party.speechiness
    }
    tracks = spotify.recommendations(seed_tracks=seeds, limit=50, **kwarg)
    tracks = tracks.get("tracks")
    return render_template("party_view.html", party=party, tracks=tracks)


@app.route("/party/new", methods=["GET", "POST"])
def new_party():
    user = get_current_user()
    if not user:
        return redirect("/")

    form = PartyRoomCreateForm(request.form)

    if not form.validate_on_submit() or request.method == "GET":
        return render_template("new_party.html", form=form)

    room_name = form.room_name.data
    room_password = form.room_password.data
    danceability = float(form.danceability.data)
    loudness = float(form.loudness.data)
    energy = float(form.energy.data)
    speechiness = float(form.speechiness.data)

    room_creator = user.id

    party = Party(creator=room_creator,
                  name=room_name,
                  password=room_password,
                  danceability=danceability,
                  loudness=loudness,
                  energy=energy,
                  speechiness=speechiness)
    party.clients.append(user)
    db.session.add(party)
    db.session.commit()

    return redirect("/party/{}".format(party.id))


@app.route("/party/join", methods=["GET", "POST"])
def join_party():
    user = get_current_user()
    if not user:
        return redirect("/")
    form = PartyRoomJoinForm(request.form)

    if not form.validate_on_submit() or request.method == "GET":
        return render_template("join_party.html", form=form)

    room_id = form.room_id.data
    room_password = form.room_password.data
    party = Party.query.get(int(room_id))

    if not party or party.password != room_password:
        return render_template("join_party.html",
                               form=form,
                               error="Incorrect Room Id or Password")

    if len(party.clients) >= MAX_CLIENTS_PER_ROOM:
        return render_template("join_party.html",
                               form=form,
                               error="Max number of clients per room exceeded")

    party.clients.append(user)
    db.session.commit()

    return redirect("/party/{}".format(party.id))


@app.route("/")
def home():
    user = get_current_user()
    parites = []
    if user:
        parites = db.session.query(Party).filter(
            Party.creator == user.id or Party.clients.any(id=user.id)).all()
    return render_template("home.html",
                           user=user,
                           spotify_url=getSPOauthURI(),
                           parties=parites)


def get_current_user():
    if session.get(Config.USER_KEY):
        user = User.query.get(session.get(Config.USER_KEY))
        refresh_token_if_necessary([user], db)
        return user
    return None


@app.route("/callback/spotify")
def spotify_callback():
    access_token = None
    refresh_token = None
    expires_at = None

    url = request.url
    code = sp_oauth.parse_response_code(url)

    if code:
        token_info = sp_oauth.get_access_token(code, check_cache=False)
        access_token = token_info['access_token']
        refresh_token = token_info['refresh_token']
        expires_at = datetime.datetime.fromtimestamp(token_info['expires_at'])

    sp_user = get_user_from_access_token(access_token)

    if not sp_user:
        return redirect("/")

    user = User.query.get(sp_user.get("id"))
    if user:
        user.access_token = access_token
        user.refesh_token = refresh_token
        user.token_expiration_time = expires_at
    else:
        user = User(id=sp_user.get("id"),
                    access_token=access_token,
                    name=sp_user.get("display_name"),
                    refresh_token=refresh_token,
                    token_expiration_time=expires_at)
        db.session.add(user)

    db.session.commit()
    session[Config.USER_KEY] = user.id
    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
