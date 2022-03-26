from app import db
from flask_login import UserMixin


# note
class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50))
    content = db.Column(db.Text)
    date = db.Column(db.DateTime)
    filePath = db.Column(db.String(200))
    pet_id = db.Column(db.Integer, db.ForeignKey('pet.id'))
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))

# association table
families = db.Table('families',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('pet_id', db.Integer, db.ForeignKey('pet.id'))
)


# user
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(15), unique=True)
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(80))
    code = db.Column(db.String(15))
    notes = db.relationship('Note', backref='author')
    pets = db.relationship('Pet', secondary=families, lazy='subquery', backref=db.backref('families', lazy=True))


# pet
class Pet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(15))
    type = db.Column(db.String(3))
    breed = db.Column(db.String(50))
    gender = db.Column(db.Boolean)
    sterilization = db.Column(db.Boolean)
    birthday = db.Column(db.Date)
    commemorationDay = db.Column(db.Date)
    weight = db.Column(db.Float)
    notes = db.relationship('Note', backref='protagonist')


