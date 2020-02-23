from flask_wtf import FlaskForm
from wtforms import TextField, SubmitField, PasswordField
from wtforms.validators import Length, Email, Required


class PartyRoomCreateForm(FlaskForm):
    room_creator = None
    room_name = TextField('What is the name of the Room?',
                          validators=[Required(), Length(max=2047)])
    room_password = PasswordField(
        "Please type a room password",
        validators=[Required(), Length(max=2047, min=6)])
    submit = SubmitField('Submit - Requires Spotify Login')


class PartyRoomJoinForm(FlaskForm):
    room_id = TextField("Please Type The Room ID", validators=[Required()])
    room_password = PasswordField(
        "Please type a room password",
        validators=[Required(), Length(max=2047, min=6)])
    submit = SubmitField('Submit - Requires Spotify Login')
