from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired


class GetFantagazzettaRequirements(FlaskForm):
    url_lega = StringField('Link Lega', validators=[DataRequired()])
    password_lega = PasswordField('Password', validators=[DataRequired()])
    millions = StringField('Fantamilioni', validators=[DataRequired()])
    submit = SubmitField('Inizia')

class GetFantagazzettaRecover(FlaskForm):
    password_recupero = StringField('Password recupero Asta', validators=[DataRequired()])
    submit = SubmitField('Recupera')

class AccettaScarti(FlaskForm):
    submit = SubmitField('SI')
