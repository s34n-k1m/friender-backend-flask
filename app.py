import os

from flask import Flask, request, session, g, abort, jsonify, make_response
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError
import jwt
from flask_cors import CORS, cross_origin

from forms import UserAddForm, LoginForm
from models import db, connect_db, User, Like, Dislike
from helpers import upload_file_to_s3
# from secret import S3_BUCKET
from werkzeug.utils import secure_filename

from dotenv import load_dotenv
load_dotenv()

CURR_USER_KEY = "curr_user"
S3_BUCKET = os.environ.get('S3_BUCKET')

app = Flask(__name__)
CORS(app)

# Get DB_URI from environ variable (useful for production/testing) or,
# if not set there, use development local db.
app.config['SQLALCHEMY_DATABASE_URI'] = (
    os.environ.get('DATABASE_URL', 'postgres:///friender'))

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = True
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', "it's a secret")
toolbar = DebugToolbarExtension(app)

connect_db(app)

INVALID_CREDENTIALS_MSG = "invalid-credentials"
INVALID_CREDENTIALS_STATUS_CODE = 400


def _get_json_message(msg, status_code):
    """ Takes a message and status code and returns JSON

        Returns:
        {
            status: "invalid-credentitials"
        }
    """
    return (jsonify(status=msg), status_code)

##############################################################################
# User signup/login/logout


@app.before_request
def add_user_to_g():
    """If we're logged in, add curr user to Flask global.
    Authorization is provided in the request header with a key of
    "Authorization" 
    """
    if "Authorization" in request.headers:
        token = request.headers["Authorization"]
        payload = jwt.decode(token, app.config.get(
            'SECRET_KEY'), algorithms=["HS256"])

        if "username" in payload:
            g.user = User.query.filter_by(username=payload["username"]).first()

    else:
        g.user = None


def do_login(user):
    """Log in user."""

    payload = {
        "username": user.username,
        "user_id": user.id
    }

    return jwt.encode(payload, app.config.get('SECRET_KEY'))


@app.route('/signup', methods=["POST"])
# @cross_origin()
def signup():
    """Handle user signup.

    Create new user and add to DB. Return JSON of new user.

    If the there already is a user with that username: return JSON
    with error message
    """

    received = request.json

    form = UserAddForm(csrf_enabled=False, data=received)

    if form.validate_on_submit():
        try:
            user = User.signup(
                username=form.username.data,
                password=form.password.data,
                email=form.email.data,
                first_name=form.first_name.data,
                last_name=form.last_name.data,
                image_url=form.image_url.data or User.image_url.default.arg,
                hobbies=form.hobbies.data,
                interests=form.interests.data,
                zip_code=form.zip_code.data,
                friend_radius_miles=form.friend_radius_miles.data,
            )
            db.session.commit()

        except IntegrityError as e:
            return _get_json_message("username-email-already-taken", INVALID_CREDENTIALS_STATUS_CODE)

        token = do_login(user)

        return (jsonify(
            user=user.serialize(),
            token=token
        ), 201)

    else:
        return _get_json_message("unable-to-add-user", INVALID_CREDENTIALS_STATUS_CODE)


@app.route('/login', methods=["POST"])
# @cross_origin()
def login():
    """Handle user login.
    Takes in JSON {username, password}
    Returns JSON {user, token} if valid

    If data is not valid, returns JSON with error message.

    """

    received = request.json
    form = LoginForm(csrf_enabled=False, data=received)
    if form.validate_on_submit():
        user = User.authenticate(form.username.data,
                                 form.password.data)

        if user:
            token = do_login(user)
            return (jsonify(
                    user=user.serialize(),
                    token=token), 201)

    return _get_json_message(INVALID_CREDENTIALS_MSG, INVALID_CREDENTIALS_STATUS_CODE)

##############################################################################
# General user routes:


@app.route('/users/<int:user_id>')
# @cross_origin()
def users_show(user_id):
    """Get a user info.
    Returns JSON: 
        {
        "user": {
            "email": "test1@test.com",
            "first_name": "test",
            "friend_radius_miles": 5,
            "hobbies": "test",
            "image_url": "/static/images/default-pic.png",
            "interests": "test",
            "last_name": "test",
            "username": "test1",
            "zip_code": "11111",
            "coordinates": "-122.42,37.76"
            }
        }
    """

    if not g.user:
        return _get_json_message(INVALID_CREDENTIALS_MSG, INVALID_CREDENTIALS_STATUS_CODE)

    user = User.query.get_or_404(user_id)

    return jsonify(user=user.serialize())


@app.route('/users/<int:user_id>/potentials')
# @cross_origin()
def get_potential_friends(user_id):
    """Get list of users that are potential friends for the current user. 

    Potential friends are ones where:
        - current user has not already liked/disliked
        - other user has not already diskliked
        - distance between users is less than both user's friend radii

    Returns JSON {user_options: [ user, ...]}
        Where user { email, first_name, last_name, friend_radius_miles, hobbies,
                    image_url, interests, username, zip_code, coordinates}

    If no user is logged in, return JSON with error message.
    """

    if not g.user:
        return _get_json_message(INVALID_CREDENTIALS_MSG, INVALID_CREDENTIALS_STATUS_CODE)

    current_user = User.query.get_or_404(user_id)

    if current_user.username != g.user.username:
        return _get_json_message(INVALID_CREDENTIALS_MSG, INVALID_CREDENTIALS_STATUS_CODE)

    user_options = User.get_list_of_potential_friends(current_user)
    user_options_serialized = [user.serialize() for user in user_options]

    return jsonify(user_options=user_options_serialized)


@app.route('/users/<int:user_id>/image-upload', methods=["POST"])
# @cross_origin()
def upload_img_to_s3(user_id):
    """Upload user image to AWS S3
    Calls helper function upload_file_to_s3
    Returns JSON {status, image_url}

    If no user is logged in, return JSON with error message.
    """

    if not g.user:
        return _get_json_message(INVALID_CREDENTIALS_MSG, INVALID_CREDENTIALS_STATUS_CODE)

    img = request.files['file']
    if img:
        # TODO: Need a way to create unique filenames so it doesn't overwrite
        # existing files with the same name in S3
        filename = secure_filename(img.filename)
        img.save(filename)
        output = upload_file_to_s3(S3_BUCKET, filename)

        # Updates the current user's image url to the uploading image
        current_user = User.query.get_or_404(user_id)
        current_user.image_url = str(output)
        db.session.commit()

        return jsonify(status="upload-successful", image_url=str(output))

    return _get_json_message("no-image", 400)


##############################################################################
# User likes/ dislikes

@app.route('/users/like/<int:other_id>', methods=['POST'])
# @cross_origin()
def like_potential_friend(other_id):
    """Like a potential friend for logged in user.
    Checks if like is in current user's list of potential friends.
    If valid, adds user to current user's potential friends and updates
    database. 

    Returns JSON {status}

    If no user is logged in, return JSON with error message.
    """

    if not g.user:
        return _get_json_message(INVALID_CREDENTIALS_MSG, INVALID_CREDENTIALS_STATUS_CODE)

    user_options = User.get_list_of_potential_friends(g.user)
    other_user = User.query.get_or_404(other_id)

    if other_user not in user_options:
        return _get_json_message("user-not-potential-friend", INVALID_CREDENTIALS_STATUS_CODE)

    g.user.likes.append(other_user)
    db.session.commit()

    return jsonify(status="user-liked")


@app.route('/users/dislike/<int:other_id>', methods=['POST'])
# @cross_origin()
def dislike_potential_friend(other_id):
    """Dislike a potential friend for logged in user.
    Checks if like is in current user's list of potential friends.
    If valid, adds user to current user's potential friends and updates
    database. 
    
    Returns JSON {status}

    If no user is logged in, return JSON with error message.
    
    """

    if not g.user:
        return _get_json_message(INVALID_CREDENTIALS_MSG, INVALID_CREDENTIALS_STATUS_CODE)

    user_options = User.get_list_of_potential_friends(g.user)
    other_user = User.query.get_or_404(other_id)

    if other_user not in user_options:
        return _get_json_message("user-not-potential-friend", INVALID_CREDENTIALS_STATUS_CODE)

    g.user.dislikes.append(other_user)
    db.session.commit()

    return jsonify(status="user-disliked")
