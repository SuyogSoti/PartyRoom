from flask_wtf import FlaskForm
from wtforms import TextField, SubmitField
from wtforms.validators import Length, Email, Required

# Form ORM
class PartyRoom(FlaskForm):
    room_name = TextField('What is the name of the Room?', validators=[Required(), Length(max=2047)] )
    submit = SubmitField('Submit')