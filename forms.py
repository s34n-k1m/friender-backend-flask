from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField
from wtforms.validators import InputRequired, Email, Length


class UserAddForm(FlaskForm):
    """Form for adding users."""

    username = StringField('Username', validators=[InputRequired()])
    password = PasswordField('Password', validators=[Length(min=6)])
    email = StringField('E-mail', validators=[InputRequired(), Email()])
    first_name = StringField('First Name', validators=[InputRequired()])
    last_name = StringField('Last Name', validators=[InputRequired()])
    image_url = StringField('(Optional) Image URL')
    hobbies = StringField('Hobbies', validators=[InputRequired()])
    interests = StringField('Interests', validators=[InputRequired()])
    zip_code = StringField('Zip Code', validators=[InputRequired()])
    friend_radius_miles = StringField('Friend Radius', validators=[InputRequired()])


class UserEditForm(FlaskForm):
    """Form for editing users."""

    image_url = StringField('(Optional) Image URL')
    password = PasswordField('Password', validators=[Length(min=6)])
    email = StringField('E-mail', validators=[InputRequired(), Email()])
    first_name = StringField('First Name', validators=[InputRequired()])
    last_name = StringField('Last Name', validators=[InputRequired()])
    hobbies = StringField('Hobbies', validators=[InputRequired()])
    interests = StringField('Interests', validators=[InputRequired()])
    zip_code = StringField('Zip Code', validators=[InputRequired()])
    friend_radius_miles = StringField('Friend Radius', validators=[InputRequired()])


class LoginForm(FlaskForm):
    """Login form."""

    username = StringField('Username', validators=[InputRequired()])
    password = PasswordField('Password', validators=[Length(min=6)])

