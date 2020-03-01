from flask import Flask
from flask_bootstrap import Bootstrap
from flask_nav import Nav
from flask_nav.elements import Navbar, View
from config import Config
import os
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship

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
    clients = relationship('User', secondary='userpartylink')
    creator = db.Column(db.String, nullable=False)
    name = db.Column(db.String, nullable=False)
    password = db.Column(db.String, nullable=False)

    danceability = db.Column(db.Float, nullable=True)
    loudness  = db.Column(db.Float, nullable=True)
    energy  = db.Column(db.Float, nullable=True)
    speechiness  = db.Column(db.Float, nullable=True)

    def __repr__(self):
        return '<Party {}>'.format(self.id)


class User(db.Model):
    id = db.Column(db.String, primary_key=True)
    access_token = db.Column(db.String, nullable=False)
    refresh_token = db.Column(db.String, nullable=False)
    token_expiration_time = db.Column(db.DateTime, nullable=False)
    parites = relationship(Party, secondary='userpartylink')
    name = db.Column(db.String, nullable=False)

    def __repr__(self):
        return '<User {}>'.format(self.id)


class UserPartyLink(db.Model):
    __tablename__ = 'userpartylink'
    party_id = db.Column(db.Integer,
                         db.ForeignKey('party.id'),
                         primary_key=True)
    client_id = db.Column(db.String,
                          db.ForeignKey('user.id'),
                          primary_key=True)


db.create_all()
