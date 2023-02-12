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
# from clubmanager.models import FinalApplicationResult
from clubmanager.functions import generate_UUID, uniqueRoles, rolespecificquestions, generalquestions, getUserOwnedClubs, generalquestions_maxlength, rolespecificquestion_maxlength
from clubmanager.flaskforms import ApplicationSelectForm

@app.route('/clubs/<uuid:ClubId>/applications/results', methods=['POST'])
def sendresults(ClubId):
    form = ApplicationSelectForm()
    mode = request.args.get('mode')
    if mode == 'sendall':
        stuff = request.form.getlist('SelectedApplicants')
        return stuff 
    else:
        return 'wrong mode'