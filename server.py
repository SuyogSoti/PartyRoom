from flask import render_template, request, redirect
from flask_helpers import app
from party_form import PartyRoom


@app.route('/party/<string:room_id>')
def party(room_id):
    return render_template("party_view.html", room={"name": "hi", "id": room_id})


@app.route("/party/new", methods=["GET", "POST"])
def new_party():
    form = PartyRoom(request.form)

    if not form.validate_on_submit() or request.method == "GET":
        return render_template("new_party.html", form=PartyRoom())

    room_name = form.room_name.data
    return redirect("/party/" + room_name)


@app.route("/")
def home():
    return render_template("home.html")


if __name__ == "__main__":
    app.run(debug=True)