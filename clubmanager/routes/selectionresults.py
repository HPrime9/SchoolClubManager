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
from clubmanager.models import Applications
from clubmanager.functions import generate_UUID, uniqueRoles, rolespecificquestions, generalquestions, getUserOwnedClubs, generalquestions_maxlength, rolespecificquestion_maxlength
from clubmanager.flaskforms import ApplicationSelectForm

@app.route('/clubs/<uuid:ClubId>/selectionresults', methods=['POST'])
def sendresults(ClubId):
    form = ApplicationSelectForm()
    mode = request.args.get('mode')
    if mode == 'sendall':
        sendemaillist = []
        AllApplicationIds = request.form.getlist('ApplicationId')
        RoleIdsSelectedFor = request.form.getlist('RoleIdSelectedFor')
        AllClubOwnerNotes = request.form.getlist('ClubOwnerNotes')
        print(AllClubOwnerNotes)
        for i in range(len(AllApplicationIds)):
            unique_applicant = Applications.query.filter_by(ApplicationId=str(AllApplicationIds[i])).first()
            unique_applicant.ClubOwnerNotes = AllClubOwnerNotes[i]
            if str(RoleIdsSelectedFor[i]) == 'None':
                unique_applicant.RoleIdSelectedFor = 'None'
                unique_applicant.EmailSent = 'No'
            else:
                unique_applicant.RoleIdSelectedFor = str(RoleIdsSelectedFor[i])
                if unique_applicant.EmailSent == 'No':
                    sendemaillist.append(str(AllApplicationIds[i]))
                    unique_applicant.EmailSent = 'Yes'
            try:
                db.session.commit()
            except:
                return redirect(url_for('get_application', ClubId=str(ClubId)) + '?mode=viewall')
        print(sendemaillist)
        return redirect(url_for('get_application', ClubId=str(ClubId)) + '?mode=viewall')



                
# # RoleIdApplyingFor = db.Column(db.String(36), nullable=False)
# # ApplicationState = db.Column(db.String(100), nullable=True) #draft submitted, accepted
# # RoleIdSelectedFor = db.Column(db.String(36), nullable=True)
# # ClubOwnerNotes = db.Column(db.String(500), nullable=True)
# # EmailSent = db.Column(db.String(5), nullable=False)
#         return stuff 
#     else:
#         return 'wrong mode'