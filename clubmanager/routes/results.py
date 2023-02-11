# Import libraries
from flask import render_template, request, url_for, redirect
from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import InputRequired, Length
from flask_login import login_required, current_user
from sqlalchemy import select
from datetime import datetime

# import custom models
from clubmanager import app, db
from clubmanager.models import Club, ClubRole, QuestionAnswer
from clubmanager.functions import generate_UUID, show_club_applications, uniqueRoles, rolespecificquestions, generalquestions, getUserOwnedClubs, generalquestions_maxlength, rolespecificquestion_maxlength
from clubmanager.flaskforms import FinalApplicationResultForm

@app.route('/clubs/<uuid:ClubId>/results', methods=['POST'])
def sendresults(ClubId):
    form = FinalApplicationResultForm()
    mode = request.args.get('mode')
    if mode == 'sendall':
        return str('hi')