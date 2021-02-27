"""Seed database with sample data from CSV Files."""

from csv import DictReader
from app import db
from models import User, Like, Dislike

db.drop_all()
db.create_all()

with open('generator/users.csv') as users:
    db.session.bulk_insert_mappings(User, DictReader(users))

with open('generator/likes.csv') as likes:
    db.session.bulk_insert_mappings(Like, DictReader(likes))

with open('generator/dislikes.csv') as dislikes:
    db.session.bulk_insert_mappings(Dislike, DictReader(dislikes))

db.session.commit()