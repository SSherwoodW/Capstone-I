from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, IntegerField, TextAreaField
from wtforms.validators import InputRequired, Email, Optional, NumberRange, URL, AnyOf, Length
from models import User
import email_validator


class UserAddForm(FlaskForm):
    """Form for adding users."""

    username = StringField('Username', validators=[InputRequired()])
    first_name = StringField('First name', validators=[InputRequired()])
    last_name = StringField('Last name', validators=[InputRequired()])
    email = StringField('E-mail', validators=[InputRequired(), Email()])
    password = PasswordField('Password', validators=[
                             InputRequired(), Length(min=8)])

    def validate(self, extra_validators=None):
        initial_validation = super(UserAddForm, self).validate()
        if not initial_validation:
            return False
        user = User.query.filter_by(email=self.email.data).first()
        if user:
            self.email.errors.append("Email already registered")
            return False
        return True


class LoginForm(FlaskForm):
    """Login form."""

    username = StringField('Username', validators=[InputRequired()])
    password = PasswordField('Password', validators=[Length(min=6)])

    def validate(self, extra_validators=None):
        initial_validation = super(LoginForm, self).validate()
        if not initial_validation:
            return False
        else:
            return True


class AddressForm(FlaskForm):
    """Address search form."""

    bedrooms = IntegerField('Bedrooms', validators=[
                            InputRequired()])
    address = StringField('Street Address', validators=[InputRequired()])
    zipcode = IntegerField('ZIP or postal code', validators=[
                           InputRequired(), Length(min=5, max=9)])
    city = StringField('City', validators=[InputRequired()])
    state = StringField('State', validators=[InputRequired()])

    def validate_on_submit(self, extra_validators=None):
        initial_validation = super(AddressForm, self).validate()
        if not initial_validation:
            return False
        else:
            return True


class FavoriteForm(FlaskForm):
    """Add search to favorites form."""

    comment = TextAreaField('Comment', validators=[
                            Optional(), Length(max=250)])
