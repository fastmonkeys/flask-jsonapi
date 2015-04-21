from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from flask_jsonapi import JSONAPI

app = Flask(__name__)
app.testing = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///memory'
app.config['SERVER_NAME'] = 'example.com'
db = SQLAlchemy(app)
jsonapi = JSONAPI()
jsonapi.init_app(app)


class Person(db.Model):
    __tablename__ = 'person'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String)
    last_name = db.Column(db.String)
    twitter = db.Column(db.String)


class Article(db.Model):
    __tablename__ = 'article'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String)
    author_id = db.Column(db.Integer, db.ForeignKey(Person.id))
    author = db.relationship(Person)


class Comment(db.Model):
    __tablename__ = 'comment'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String)
    article_id = db.Column(db.Integer, db.ForeignKey(Article.id))
    article = db.relationship(Article, backref='comments')
