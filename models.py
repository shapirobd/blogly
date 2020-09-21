"""Models for Blogly."""
import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(db.Model):

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    first_name = db.Column(db.Text, nullable=False)

    last_name = db.Column(db.Text, nullable=False)

    image_url = db.Column(db.Text, nullable=False,
                          default='https://plumepoetry.com/wp-content/uploads/2019/12/default-profile.png')

    posts = db.relationship("Post", backref="user",
                            cascade="all, delete-orphan")


class Post(db.Model):

    __tablename__ = 'posts'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    title = db.Column(db.Text, nullable=False)

    content = db.Column(db.Text, nullable=False)

    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.datetime.now)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    posttags = db.relationship("PostTag", backref="post",
                               cascade="all, delete-orphan")


class Tag(db.Model):

    __tablename__ = 'tags'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    name = db.Column(db.Text, nullable=False, unique=True)

    posttags = db.relationship("PostTag", backref="tag",
                               cascade="all, delete-orphan")


class PostTag(db.Model):

    __tablename__ = 'posttags'

    tag_id = db.Column(db.Integer, db.ForeignKey(
        'tags.id'), primary_key=True, nullable=False)

    post_id = db.Column(db.Integer, db.ForeignKey(
        'posts.id'), primary_key=True, nullable=False)


def connect_db(app):
    db.app = app
    db.init_app(app)
