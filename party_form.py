from flask_wtf import FlaskForm
from wtforms import TextField, SubmitField, PasswordField
import wtforms
from wtforms.validators import Length, Email, Required, NumberRange


class PartyRoomCreateForm(FlaskForm):
    room_creator = None
    room_name = TextField('What is the name of the Room?',
                          validators=[Required(), Length(max=2047)])
    room_password = PasswordField(
        "Please type a room password",
        validators=[Required(), Length(max=2047, min=6)])
    danceability = wtforms.FloatField("How danceable should the songs be between 0 and 1", validators=[NumberRange(min=0, max=1)])
    loudness = wtforms.FloatField("How loud should the songs be between 0 and 1", validators=[NumberRange(min=0, max=1)])
    energy = wtforms.FloatField("How energetic should the songs be between 0 and 1", validators=[NumberRange(min=0, max=1)])
    speechiness = wtforms.FloatField("How wordy should the songs be between 0 and 1", validators=[NumberRange(min=0, max=1)])
    submit = SubmitField('Submit - Requires Spotify Login')


class PartyRoomJoinForm(FlaskForm):
    room_id = TextField("Please Type The Room ID", validators=[Required()])
    room_password = PasswordField(
        "Please type a room password",
        validators=[Required(), Length(max=2047, min=6)])
    submit = SubmitField('Submit - Requires Spotify Login')
