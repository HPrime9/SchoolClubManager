# Import libraries
from flask_login import UserMixin
from datetime import datetime
from . import db

# Create student data table
class Student(UserMixin, db.Model):
    id = db.Column(db.String(36), primary_key=True)
    FirstName = db.Column(db.String(100), nullable=False)
    LastName = db.Column(db.String(100), nullable=False)
    Username = db.Column(db.String(30), unique=True, nullable=False)
    StudentNum = db.Column(db.Integer, unique=True, nullable=False)
    Email = db.Column(db.String(55), unique=True, nullable=False)
    Password = db.Column(db.String(80), nullable=False)
    Grade = db.Column(db.Integer, nullable=False)
    School = db.Column(db.String(40), nullable=False)
    Date_Joined = db.Column(db.Date, default=datetime.utcnow)

