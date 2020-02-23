from flask import render_template, request, redirect, session
import json
import requests
from flask_helpers import app, db, Party
from party_form import PartyRoomCreateForm, PartyRoomJoinForm
from spotify import sp_oauth, getSPOauthURI, get_user_from_access_token
import spotipy
import random
from config import Config


@app.route('/party/<int:room_id>')
def party(room_id):
    if not session.get(Config.USER_KEY):
        return redirect("/")

    party = Party.query.get(int(room_id))
    if not party:
        return redirect("/")
    
    ids = json.loads(party.client_ids)
    spotify = spotipy.Spotify(session.get(Config.USER_KEY))
    tracks = spotify.current_user_top_tracks(limit=1000).get("items", [])
    random.shuffle(tracks)
    return render_template("party_view.html", party=party, tracks=tracks)


@app.route("/party/new", methods=["GET", "POST"])
def new_party():
    if not session.get(Config.USER_KEY):
        return redirect("/")

    form = PartyRoomCreateForm(request.form)

    if not form.validate_on_submit() or request.method == "GET":
        return render_template("new_party.html", form=form)

    room_name = form.room_name.data
    room_password = form.room_password.data
    user = get_user_from_access_token(session.get(Config.USER_KEY))
    room_creator = user.get("id")
    party = Party(creator=room_creator,
                  name=room_name,
                  client_ids=json.dumps([room_creator]),
                  password=room_password)
    db.session.add(party)
    db.session.commit()
    return redirect("/party/{}".format(party.id))


@app.route("/party/join", methods=["GET", "POST"])
def join_party():
    if not session.get(Config.USER_KEY):
        return redirect("/")
    form = PartyRoomJoinForm(request.form)

    if not form.validate_on_submit() or request.method == "GET":
        return render_template("join_party.html", form=form)

    room_id = form.room_id.data
    room_password = form.room_password.data
    user = get_user_from_access_token(session.get(Config.USER_KEY))
    current_user = user.get("id")
    party = Party.query.get(int(room_id))
    
    if not party or party.password != room_password:
        return redirect("/party/join")

    ids = json.loads(party.client_ids)
    ids.append(current_user)
    party.client_ids = json.dumps(list(set(ids)))
    db.session.commit()
    
    return redirect("/party/{}".format(party.id))


@app.route("/")
def home():
    user = get_user_from_access_token(session.get(Config.USER_KEY))
    parites = []
    if user:
        parites = db.session.query(Party).filter(Party.creator == user.get("id")).all()
    return render_template("home.html", user=user, spotify_url=getSPOauthURI(), parties=parites)


@app.route("/callback/spotify")
def spotify_callback():
    access_token = None

    token_info = sp_oauth.get_cached_token()

    if token_info:
        access_token = token_info['access_token']
    else:
        url = request.url
        code = sp_oauth.parse_response_code(url)
        if code:
            token_info = sp_oauth.get_access_token(code)
            access_token = token_info['access_token']

    session[Config.USER_KEY] = access_token
    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)