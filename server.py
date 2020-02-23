from flask import render_template, request
from flask_helpers import app
from party_form import PartyRoom


@app.route('/party/:room')
def party():
    return 'Hello, World!'


@app.route("/party/new", methods=["GET", "POST"])
def new_party():
    form = PartyRoom(request.form)

    if not form.validate_on_submit() or request.method != "POST":
        return render_template("new_party.html", form=PartyRoom())

    room_name = form.room_name.data
    return 'Submitted!'


@app.route("/")
def home():
    return render_template("home.html")


if __name__ == "__main__":
    app.run(debug=True)