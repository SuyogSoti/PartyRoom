from flask import Flask
from flask_bootstrap import Bootstrap
from flask_nav import Nav
from flask_nav.elements import Navbar, View
from config import Config
import os
from flask_sqlalchemy import SQLAlchemy

nav = Nav()

app = Flask(__name__)
app.config.from_object(Config)
Bootstrap(app)
nav.init_app(app)
app.secret_key = os.environ.get("SECRET_KEY", os.urandom(24))
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DB_URL")
db = SQLAlchemy(app)


@nav.navigation()
def mynavbar():
    return Navbar('Party Room', View('Home', 'home'),
                  View('New Party', 'new_party'),
                  View('Join Party', 'join_party'))


class Party(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    client_ids = db.Column(db.String, nullable=False)
    creator = db.Column(db.String, nullable=False)
    name = db.Column(db.String, nullable=False)
    password = db.Column(db.String, nullable=False)
    

    def __repr__(self):
        return '<Party {}>'.format(self.id)

db.create_all()