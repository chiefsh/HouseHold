from core.form import Form
from wtforms import StringField, IntegerField, FloatField
from wtforms.fields.html5 import TelField
from wtforms.validators import Length, required, email, optional


class AccountLoginForm(Form):
    username = StringField('name', [Length(min=2, max=25), required()])
    password = StringField('password', [Length(min=8, max=25), required()])



