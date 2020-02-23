from flask import render_template, request, redirect, session
import json
import requests
from flask_helpers import app, db, Party, User
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
    
    tracks = []

    room_id = str(room_id)
    session["parties"] = session.get("parties", {})
    if room_id not in session["parties"]:
        session["parties"][room_id] = [session.get(Config.USER_KEY)]

    for client in party.clients:
        spotify = spotipy.Spotify(client.access_token)
        tracks += list(spotify.current_user_top_tracks(limit=10).get("items", []))
    
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
    user = get_current_user()
    room_creator = user.id

    party = Party(creator=room_creator,
                  name=room_name,
                  password=room_password)
    party.clients.append(user)
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
    party = Party.query.get(int(room_id))
    
    if not party or party.password != room_password:
        return render_template("join_party.html", form=form)

    user = get_current_user()
    party.clients.append(user)
    db.session.commit()
    
    return redirect("/party/{}".format(party.id))


@app.route("/")
def home():
    user = get_current_user()
    parites = []
    if user:
        parites = db.session.query(Party).filter(Party.creator == user.id).all()
    return render_template("home.html", user=user, spotify_url=getSPOauthURI(), parties=parites)



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
        user = User(id=sp_user.get("id"), access_token=access_token, name=sp_user.get("display_name"))
        db.session.add(user)

    db.session.commit()
    session[Config.USER_KEY] = user.id
    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")