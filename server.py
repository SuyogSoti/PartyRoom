from flask import render_template, request, redirect, session
import requests
from flask_helpers import app
from party_form import PartyRoomCreateForm, PartyRoomJoinForm
from spotify import sp_oauth, getSPOauthURI, get_user_from_access_token
import spotipy
from config import Config


@app.route('/party/<string:room_creator>/<string:room_name>')
def party(room_creator, room_name):
    if not session.get(Config.USER_KEY):
        return redirect("/")

    return render_template("party_view.html",
                           room={
                               "name": room_name,
                               "creator": room_creator
                           })


@app.route("/party/new", methods=["GET", "POST"])
def new_party():
    if not session.get(Config.USER_KEY):
        return redirect("/")

    form = PartyRoomCreateForm(request.form)

    if not form.validate_on_submit() or request.method == "GET":
        return render_template("new_party.html", form=form)

    room_name = form.room_name.data
    user = get_user_from_access_token(session.get(Config.USER_KEY))
    room_creator = user.get("id")
    return redirect("/party/{}/{}".format(room_creator, room_name))


@app.route("/party/join", methods=["GET", "POST"])
def join_party():
    if not session.get(Config.USER_KEY):
        return redirect("/")
    form = PartyRoomJoinForm(request.form)

    if not form.validate_on_submit() or request.method == "GET":
        return render_template("join_party.html", form=form)

    room_name = form.room_name.data
    room_creator = form.room_creator.data
    return redirect("/party/{}/{}".format(room_creator, room_name))


@app.route("/")
def home():
    user = get_user_from_access_token(session.get(Config.USER_KEY))
    return render_template("home.html", user=user, spotify_url=getSPOauthURI())


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