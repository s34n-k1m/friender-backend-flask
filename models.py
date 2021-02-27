"""SQLAlchemy models for Friender."""

from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
# from secret import MAPBOX_API_TOKEN
import requests
from geopy.distance import geodesic
import os
MAPBOX_API_TOKEN=os.environ.get('MAPBOX_API_TOKEN')

bcrypt = Bcrypt()
db = SQLAlchemy()

MAPBOX_API_BASE_URL = 'https://api.mapbox.com'


class Like(db.Model):
    """Connection of a user <-> liked_user."""

    __tablename__ = 'likes'

    liker_user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete="cascade"),
        primary_key=True,
    )

    liked_user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete="cascade"),
        primary_key=True,
    )

class Dislike(db.Model):
    """Connection of a user <-> disliked_user."""

    __tablename__ = 'dislikes'

    disliker_user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete="cascade"),
        primary_key=True,
    )

    disliked_user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete="cascade"),
        primary_key=True,
    )

class User(db.Model):
    """User in the system."""

    __tablename__ = 'users'

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    email = db.Column(
        db.Text,
        nullable=False,
        unique=True,
    )

    username = db.Column(
        db.String(20),
        nullable=False,
        unique=True,
    )

    password = db.Column(
        db.Text,
        nullable=False,
    )

    first_name = db.Column(
        db.String(20),
        nullable=False,
    )

    last_name = db.Column(
        db.String(20),
        nullable=False,
    )

    image_url = db.Column(
        db.Text,
        default="/static/images/default-pic.png",
    )

    hobbies = db.Column(
        db.Text,
        nullable=False,
    )
    
    interests = db.Column(
        db.Text,
        nullable=False,
    )

    zip_code = db.Column(
        db.String(5),
        nullable=False,
    )

    coordinates = db.Column(
        db.Text,
        nullable=False,
    )
    
    friend_radius_miles = db.Column(
        db.Integer,
        nullable=False,
    )

    likes = db.relationship(
        "User",
        secondary="likes",
        primaryjoin=(Like.liker_user_id == id),
        secondaryjoin=(Like.liked_user_id == id)
    )

    liked_by = db.relationship(
        "User",
        secondary="likes",
        primaryjoin=(Like.liked_user_id == id),
        secondaryjoin=(Like.liker_user_id == id)
    )

    dislikes = db.relationship(
        "User",
        secondary="dislikes",
        primaryjoin=(Dislike.disliker_user_id == id),
        secondaryjoin=(Dislike.disliked_user_id == id)
    )

    disliked_by = db.relationship(
        "User",
        secondary="dislikes",
        primaryjoin=(Dislike.disliked_user_id == id),
        secondaryjoin=(Dislike.disliker_user_id == id)
    )


    ############ GENERAL METHODS################################################################

    def __repr__(self):
        return f"<User #{self.id}: {self.username}, {self.email}>"

    def serialize(self):
        """Serialize to dictionary."""
        return { 
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "image_url": self.image_url,
            "hobbies": self.hobbies,
            "interests": self.interests,
            "zip_code": self.zip_code,
            "coordinates": self.coordinates,
            "friend_radius_miles": self.friend_radius_miles,
        }

    ############ LIKE/DISLIKE METHODS ########################################################

    def is_liked_by(self, other_user):
        """Is this user liked by `other_user`?"""

        # found_user_list = [user for user in self.liked_by if user == other_user]
        return any([user for user in self.liked_by if user == other_user])

    def is_liking(self, other_user):
        """Is this user liking `other_user`?"""

        # found_user_list = [user for user in self.likes if user == other_user]
        # return len(found_user_list) == 1
        return any([user for user in self.likes if user == other_user])
    
    def is_disliked_by(self, other_user):
        """Is this user disliked by `other_user`?"""

        # found_user_list = [user for user in self.disliked_by if user == other_user]
        # return len(found_user_list) == 1
        return any([user for user in self.disliked_by if user == other_user])

    def is_disliking(self, other_user):
        """Is this user disliking `other_user`?"""

        # found_user_list = [user for user in self.dislikes if user == other_user]
        # return len(found_user_list) == 1
        return any([user for user in self.dislikes if user == other_user])

    ############ DISTANCE METHODS ##########################################################

    def is_outside_self_radius(self, other_user, distance):
        """Is the distance between user and other user greater than this user's
        friend radius? """
        return True if (distance > self.friend_radius_miles) else False

    def is_outside_other_radius(self, other_user, distance):
        """Is the distance between user and other user greater than the other
        user's friend radius? """
        return True if (distance > other_user.friend_radius_miles) else False

    def calculate_distance(self, other_user):
        """ Given a different user, calculate the direct distance in miles
        between the two """
        coordSelf = self.coordinates.split(',')
        coordOther = other_user.coordinates.split(',')

        coordSelfCalc = (float(coordSelf[1]), float(coordSelf[0]))
        coordOtherCalc = (float(coordOther[1]), float(coordOther[0]))

        return geodesic(coordSelfCalc, coordOtherCalc).miles

    @classmethod
    def get_coords(self, zip_code):
        """ Gets the longitude, latitude of the Zip Code """
        response = requests.get(f"{MAPBOX_API_BASE_URL}/geocoding/v5/mapbox.places/{zip_code}.json?access_token={MAPBOX_API_TOKEN}")
        r = response.json()

        coords = r["features"][0]["center"]

        return f"{coords[0]},{coords[1]}" 

    ############ POTENTIAL FRIENDS METHODS ###################################################

    def is_potential(self, other_user):
        """ Is this user a potential match? """

        distance = self.calculate_distance(other_user)

        if (self.is_liking(other_user) or 
            self.is_disliked_by(other_user) or
            self.is_disliking(other_user) or
            self.id == other_user.id or
            self.is_outside_self_radius(other_user, distance) or
            self.is_outside_other_radius(other_user, distance)):
            return False
        else:
            return True

    @classmethod
    def get_list_of_potential_friends(cls, current_user):
        """ Given the current user, return a list of all potential friends. """

        users = cls.query.all()

        def filterUsers(user):
            return current_user.is_potential(user)

        return list(filter(filterUsers, users))

    ############ AUTHENTICATION METHODS ###################################################

    @classmethod
    def signup(cls,
                username,
                email,
                password,
                first_name,
                last_name,
                image_url,
                hobbies,
                interests,
                zip_code,
                friend_radius_miles):
        """Sign up user.

        Hashes password and adds user to system.
        """

        hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')
        coordinates = cls.get_coords(zip_code)

        user = User(
            username=username,
            email=email,
            password=hashed_pwd,
            first_name=first_name,
            last_name=last_name,
            image_url=image_url,
            hobbies=hobbies,
            interests=interests,
            zip_code=zip_code,
            coordinates=coordinates,
            friend_radius_miles=friend_radius_miles,
        )

        db.session.add(user)
        return user

    @classmethod
    def authenticate(cls, username, password):
        """Find user with `username` and `password`.

        This is a class method (call it on the class, not an individual user.)
        It searches for a user whose password hash matches this password
        and, if it finds such a user, returns that user object.

        If can't find matching user (or if password is wrong), returns False.
        """

        user = cls.query.filter_by(username=username).first()

        if user:
            is_auth = bcrypt.check_password_hash(user.password, password)
            if is_auth:
                return user

        return False

def connect_db(app):
    """Connect this database to provided Flask app.

    You should call this in your Flask app.
    """

    db.app = app
    db.init_app(app)
