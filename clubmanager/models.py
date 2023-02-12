# Import libraries
from flask_login import UserMixin
from datetime import datetime

# Import custom libraries
from clubmanager import db

# Create student data table
class Students(UserMixin, db.Model):
    id = db.Column(db.String(36), primary_key=True)
    FirstName = db.Column(db.String(75), nullable=False)
    LastName = db.Column(db.String(100), nullable=False)
    Username = db.Column(db.String(36), unique=True, nullable=False)
    StudentNum = db.Column(db.Integer, unique=True, nullable=False)
    Email = db.Column(db.String(75), unique=True, nullable=False)
    Password = db.Column(db.String(80), nullable=False)
    Grade = db.Column(db.Integer, nullable=False)
    School = db.Column(db.String(40), nullable=False)
    Date_Joined = db.Column(db.Date, default=datetime.utcnow)

# Create club data table
class Clubs(UserMixin, db.Model):
    ClubId = db.Column(db.String(36), primary_key=True)
    StudentId = db.Column(db.Integer, nullable=False)
    School = db.Column(db.String(40), nullable=False)
    ClubName = db.Column(db.String(50), nullable=False)
    ClubDescription = db.Column(db.String(300), nullable=False)
    AppStartDate = db.Column(db.Date, nullable=False)
    AppEndDate = db.Column(db.Date, nullable=False)
    ClubContactEmail = db.Column(db.String(75), unique=True, nullable=False)
    Date_Club_Created = db.Column(db.Date, default=datetime.utcnow)
    
# Create club-student data table
class ClubStudentMaps(UserMixin, db.Model):
    ClubStudentMapId = db.Column(db.String(36), primary_key=True)
    StudentId = db.Column(db.String(36), nullable=False)
    ClubId = db.Column(db.String(36), unique=True, nullable=False)
    Date_ClubStudentMap_Created = db.Column(db.Date, default=datetime.utcnow)

# Create question data tables
class ApplicationQuestions(UserMixin, db.Model):
    ApplicationQuestionId = db.Column(db.String(36), primary_key=True)
    ClubId = db.Column(db.String(36), nullable=True)
    RoleId = db.Column(db.String(36), nullable=True)
    OrderNumber = db.Column(db.Integer, nullable=True)
    Question = db.Column(db.String(600), nullable=True)
    LengthOfResponse = db.Column(db.Integer, nullable=True)
    Date_Question_Created = db.Column(db.Date, default=datetime.utcnow)

# Create answer data table
class QuestionAnswers(UserMixin, db.Model):
    QuestionAnswerId = db.Column(db.String(36), primary_key=True)
    StudentId = db.Column(db.String(36), nullable=False)
    ClubId = db.Column(db.String(36), nullable=False)
    RoleId = db.Column(db.String(36), nullable=True)
    ApplicationQuestionId = db.Column(db.String(36), nullable=False)
    Answer = db.Column(db.String(5000), nullable=True)
    Date_Answer_Created = db.Column(db.Date, default=datetime.utcnow)

# Create role data table
class ClubRoles(UserMixin, db.Model):
    RoleId = db.Column(db.String(36), primary_key=True)
    ClubId = db.Column(db.String(36), nullable=True)
    Role = db.Column(db.String(100), nullable=True)
    RoleDescription = db.Column(db.String(500), nullable=True)
    Date_Role_Created = db.Column(db.Date, default=datetime.utcnow)

# Create announcement table
class Announcements(UserMixin, db.Model):
    AnnouncementId = db.Column(db.String(36), primary_key=True)
    ClubId = db.Column(db.String(36), nullable=False)
    Header = db.Column(db.String(100), nullable=False)
    Message = db.Column(db.String(2000), nullable=False)

# Create applicants table
class Applications(UserMixin, db.Model):
    ApplicationId = db.Column(db.String(36), primary_key=True)
    StudentId = db.Column(db.String(36), nullable=False)
    ClubId = db.Column(db.String(36), nullable=False)
    RoleIdApplyingFor = db.Column(db.String(36), nullable=False)
    ApplicationState = db.Column(db.String(100), nullable=True) #draft submitted, accepted
    RoleIdSelectedFor = db.Column(db.String(36), nullable=True)
    ClubOwnerNotes = db.Column(db.String(500), nullable=True)
    EmailSent = db.Column(db.String(5), nullable=False)

