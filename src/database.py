from datetime import datetime
from enum import unique
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow

db = SQLAlchemy()
ma = Marshmallow()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False)
    passw_hash = db.Column(db.Text, nullable=False)
    level_id = db.Column(db.Integer, db.ForeignKey('level.id'), nullable=False)

    
    def __repr__(self) -> str:
        return f"<<{self.name}: {self.username}>>"


class UserSchema(ma.Schema):
    class Meta:
        fields = ('id', 'name', 'username', 'level_id')



class Level(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    user = db.relationship('User', backref='level', lazy=True)


    def __repr__(self) -> str:
        return f"<<Level: {self.name}>>"


class LevelSchema(ma.Schema):
    class Meta:
        fields = ('id', 'name')


######################## DAIRY FARM ################################
class Gender(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), unique=True, nullable=False)
    cows = db.relationship('Cow', backref='gender')

    def __repr__(self) -> str:
        return f"<<{self.name}>>"


class GenderSchema(ma.Schema):
    class Meta:
        fields = ('id', 'name')


class Breed(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), unique=True, nullable=False)
    cows = db.relationship('Cow', backref='breed')
    
    def __repr__(self) -> str:
        return f"<<Breed: {self.name}>>"


class BreedSchema(ma.Schema):
    class Meta:
        fields = ('id', 'name')


class Cow(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    dob = db.Column(db.DateTime, nullable=False)
    milk = db.Column(db.Integer, nullable=False, default=0)
    created_at = db.Column(db.DateTime(), default=datetime.utcnow())
    updated_at = db.Column(db.DateTime(), default=datetime.utcnow())
    
    breed_id = db.Column(db.Integer, db.ForeignKey('breed.id'), nullable=False)
    gender_id = db.Column(db.Integer, db.ForeignKey('gender.id'), nullable=False)


    def __repr__(self) -> str:
        return f"<<Name: {self.name}>>"


class CowSchema(ma.Schema):
    class Meta:
        fields = ('id', 'name', 'dob', 'created_at', 'updated_at', 'breed_id', 'gender_id', 'milk')