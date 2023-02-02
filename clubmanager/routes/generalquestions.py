# Import libraries
from flask import render_template, redirect, url_for, request
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField
from wtforms.validators import InputRequired, Email, Length
from flask_login import login_required, current_user
from sqlalchemy import delete

# Import custom libraries
from clubmanager import app, db
from clubmanager.models import Club, ClubStudentMap, ApplicationQuestions, ClubRole, Announcement
from clubmanager.functions import generate_UUID, uniqueRoles, rolespecificquestions

# Create class
class ClubGeneralQuestionForm(FlaskForm):
    GeneralQuestions = StringField('General Questions', validators=[Length(max=1000)])
    GeneralQuestionsLengthOfResponse = IntegerField('Length Of Response')
    GeneralQuestionOrderNumbers = IntegerField('Question Order')
    