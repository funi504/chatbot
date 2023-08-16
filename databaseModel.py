from flask_sqlalchemy import SQLAlchemy
from uuid import uuid4

db = SQLAlchemy()

def get_uuid():
    return uuid4().hex

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.String(32) , primary_key=True , unique=True , default=get_uuid)
    email = db.Column(db.String(345), unique=True)
    domain = db.Column(db.Text ,unique=True , nullable=False)
    password = db.Column(db.Text , nullable=False)
    created_on = db.Column(db.DateTime, nullable=True)
    confirmed = db.Column(db.Boolean, nullable=False, default=False)
    confirmed_on = db.Column(db.DateTime, nullable=True)

class Project(db.Model):

    __tablename__ = "project"
    project_id = db.Column(db.String(32) , primary_key=True , unique=True , default=get_uuid)
    user_id =db.Column(db.String(32) )
    project_name = db.Column(db.String(50) , nullable=False)
    created_on = db.Column(db.DateTime, nullable=True)

class EmailConfig(db.Model):

    __tablename__ = "emailConfig"
    id = db.Column(db.String(32) , primary_key=True , unique=True , default=get_uuid)
    project_id = db.Column(db.String(32) )
    user_id = db.Column(db.String(32) )
    email = db.Column(db.String(50) , nullable=False)
    provider = db.Column(db.String(50) , nullable=False)
    password = db.Column(db.String(50) , nullable=False)
    created_on = db.Column(db.DateTime, nullable=True)