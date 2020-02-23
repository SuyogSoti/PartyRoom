from flask import Flask
from flask_bootstrap import Bootstrap
from flask_nav import Nav
from flask_nav.elements import Navbar, View
from config import Config
import os

nav = Nav()

app = Flask(__name__)
app.config.from_object(Config)
Bootstrap(app)
nav.init_app(app)
app.secret_key = os.environ.get("SECRET_KEY", os.urandom(24))


@nav.navigation()
def mynavbar():
    return Navbar(
        'Party Room',
        View('Home', 'home'),
        View('New Party', 'new_party'),
        View('Join Party', 'join_party')
    )
