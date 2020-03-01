from flask import render_template, request, redirect, session, jsonify
import json
import requests
from flask_helpers import app, db, Party, User
from party_form import PartyRoomCreateForm, PartyRoomJoinForm
from spotify import sp_oauth, getSPOauthURI, get_user_from_access_token
import spotipy
from config import Config


@app.route("/dish/data")
def dish():
    user = get_current_user()
    if not user:
        return redirect("/")

    spotify = spotipy.Spotify(user.access_token)
    tracks = []
    try:
        tracks += list(
            spotify.current_user_top_tracks(limit=100).get("items", []))
    except Exception as e:
        return render_template("/")
    return jsonify(tracks)


@app.route('/party/<int:room_id>')
def party(room_id):
    user = get_current_user()
    if not user:
        return redirect("/")

    party = Party.query.get(int(room_id))
    if not party:
        return redirect("/")

    tracks = set()

    number_of_songs_to_store = 100
    songs_per_client = int(number_of_songs_to_store / len(party.clients))
    for client in party.clients:
        spotify = spotipy.Spotify(client.access_token)
        try:
            user_tracks = set(
                spotify.current_user_top_tracks(
                    limit=number_of_songs_to_store).get("items", []))
            if not tracks:
                tracks = user_tracks
            elif tracks.isdisjoint(user_tracks):
                list_tracks = list(tracks)
                list_user_tracks = list(user_tracks)
                tracks = set(list_tracks[:number_of_songs_to_store -
                                         songs_per_client] +
                             list_user_tracks[:songs_per_client])
            else:
                tracks.intersection_update(user_tracks)
        except Exception as e:
            pass

    if not tracks:
        return redirect("/")

    spotify = spotipy.Spotify(user.access_token)
    seeds = [track.get("uri") for idx, track in enumerate(tracks) if idx < 5]
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
        return render_template("join_party.html", form=form)

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
        return User.query.get(session.get(Config.USER_KEY))
    return None


@app.route("/callback/spotify")
def spotify_callback():
    access_token = None

    url = request.url
    code = sp_oauth.parse_response_code(url)

    if code:
        token_info = sp_oauth.get_access_token(code, check_cache=False)
        access_token = token_info['access_token']

    sp_user = get_user_from_access_token(access_token)

    if not sp_user:
        return redirect("/")

    user = User.query.get(sp_user.get("id"))
    if user:
        user.access_token = access_token
    else:
        user = User(id=sp_user.get("id"),
                    access_token=access_token,
                    name=sp_user.get("display_name"))
        db.session.add(user)

    db.session.commit()
    session[Config.USER_KEY] = user.id
    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")