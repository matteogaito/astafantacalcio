from app import db

from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy_utils import PasswordType

Base = declarative_base()

class Leghe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    path_xls = db.Column(db.String(50))
    password = db.Column(db.String(100))
    millions = db.Column(db.Integer)
    url_teams = db.Column(db.String(100))
    status = db.Column(db.String(10))

class Teams(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    leghe_id = db.Column(db.Integer, db.ForeignKey('leghe.id'))
    millions = db.Column(db.Integer)

def create_all():
    db.create_all()
