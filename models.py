"""SQLAlchemy Models for MoveIn"""

from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy

bcrypt = Bcrypt()
db = SQLAlchemy()


class User(db.Model):
    """User in the system."""

    __tablename__ = 'users'

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    email = db.Column(
        db.Text,
        nullable=False,
        unique=True
    )

    username = db.Column(
        db.Text,
        nullable=False,
        unique=True
    )

    first_name = db.Column(
        db.Text,
        nullable=False
    )

    last_name = db.Column(
        db.Text,
        nullable=False
    )

    location = db.Column(
        db.Text
    )

    password = db.Column(
        db.Text,
        nullable=False
    )

    def __repr__(self):
        return f"<User {self.id}: {self.username}, {self.email}>"

    @classmethod
    def signup(cls, username, first_name, last_name, email, password):
        """Sign up user. Hash password, add user to system."""

        hashed_pw = bcrypt.generate_password_hash(password).decode('UTF-8')

        user = User(
            username=username,
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=hashed_pw,
        )

        db.session.add(user)
        return user

    @classmethod
    def authenticate(cls, username, password):
        """Find user with 'username' and 'password'.
        Searches for a user whose password hash matches this password
        and return that user object.

        if it can't find matching user/password is wrong, return False."""

        user = cls.query.filter_by(username=username).first()

        if user:
            is_auth = bcrypt.check_password_hash(user.password, password)
            if is_auth:
                return user

        return False


class City(db.Model):
    """A U.S. city."""

    __tablename__ = 'cities'

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    name = db.Column(
        db.Text,
        nullable=False
    )

    state_id = db.Column(
        db.Integer,
        db.ForeignKey('states.id', ondelete='cascade'),
        nullable=False
    )

    state = db.relationship('State')

    @classmethod
    def get_or_create(cls, name):
        exists = db.session.query(State.name).filter_by(name=name).first()
        if exists is None:
            new_state = State(name=name)
            db.session.add(new_state)
            db.session.commit()
        else:
            name = exists


class State(db.Model):
    """A U.S. state."""

    __tablename__ = 'states'

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    name = db.Column(
        db.Text,
        nullable=False,
        unique=True
    )

    city = db.relationship('City')

    @classmethod
    def get_or_create(cls, name):
        exists: db.session.query(State.id).filter_by(name=name).scalar()
        if exists:
            return db.session.query(State).filter_by(name=name).first()
        return cls(name=name)


class Location(db.Model):
    """Instance of a user search."""

    __tablename__ = 'locations'

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    street_address = db.Column(
        db.String(150),
        nullable=False
    )

    zip_code = db.Column(
        db.Integer,
        nullable=False
    )

    city_id = db.Column(
        db.Integer,
        db.ForeignKey('cities.id', ondelete='cascade')
    )

    bedrooms = db.Column(
        db.Integer,
        nullable=False
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='cascade')
    )


class Favorite(db.Model):
    """Mapping user saved seraches to locations."""

    __tablename__ = 'favorites'

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    rent_average = db.Column(
        db.Integer,
        nullable=False
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='cascade')
    )

    location_id = db.Column(
        db.Integer,
        db.ForeignKey('locations.id', ondelete='cascade')
    )


def connect_db(app):
    """Connect database to Flask app. Call this in Flask app."""

    db.app = app
    db.init_app(app)
