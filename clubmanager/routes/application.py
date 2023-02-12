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
from clubmanager.models import Clubs, ClubRoles, QuestionAnswers
from clubmanager.functions import generate_UUID, uniqueRoles, rolespecificquestions, generalquestions, getUserOwnedClubs, generalquestions_maxlength, rolespecificquestion_maxlength
from clubmanager.flaskforms import ClubApplicationForm, FinalApplicationResultForm

@app.route('/clubs/<uuid:ClubId>/applications', methods=['GET'])
@app.route('/clubs/<uuid:ClubId>/applications/<uuid:StudentId>', methods=['GET'])
@login_required
def get_application(ClubId, StudentId = ''):
    mode = request.args.get('mode')
    global selectedrole_str, selectedrole_id
    generalquestions_to_display = []
    generalquestions_maxlengths = generalquestions_maxlength(ClubId) 
    if mode == 'viewall':
        userClubCatalogue = getUserOwnedClubs(current_user.id)
        return render_template('responseoverview.html', userClubCatalogue=userClubCatalogue, ClubId=ClubId)
    elif mode == 'view' or mode == 'selectrole':
        if current_user.id == StudentId:
            checkapplicationstartdate = Clubs.query.filter_by(ClubId=str(ClubId)).first().AppStartDate
            checkapplicationenddate = Clubs.query.filter_by(ClubId=str(ClubId)).first().AppEndDate
            if datetime.now().date() >= checkapplicationstartdate and datetime.now().date() <= checkapplicationenddate:
                return 'abx'
    #             Applications(UserMixin, db.Model):
    # ApplicationId = db.Column(db.String(36), primary_key=True)
    # StudentId = db.Column(db.String(36), nullable=False)
    # ClubId = db.Column(db.String(36), nullable=False)
    # RoleIdApplyingFor = db.Column(db.String(36), nullable=False)
    # ApplicationState = db.Column(db.String(100), nullable=False) #draft submitted, accepted
    # RoleIdSelectedFor = db.Column(db.String(36), nullable=True)
    # ClubOwnerNotes = db.Column(db.String(500), nullable=False)
    # EmailSent = db.Column(db.String(5), nullable=False)
    else:
        return 'error in application'

@app.route('/clubs/<uuid:ClubId>/applications/<int:StudentNum>', methods=['POST'])
@login_required
def save_submit_application(ClubId, StudentNum):
    mode = request.args.get('mode')
    global selectedrole_str, selectedrole_id
    generalquestions_maxlengths = generalquestions_maxlength(ClubId)
    if mode == 'save':
        form = ClubApplicationForm()
        general_questions, generalquestions_id = generalquestions(ClubId)
        rolespecificquestions_to_display, rolespecificquestions_id = rolespecificquestions(str(selectedrole_id))
        if request.form.get('SubmitApplication') == 'submitapplication':
            status = 'submitted'
        else:
            status = 'draft'
        for i in range(len(general_questions)):
            answer_generalquestion = request.form[str(generalquestions_id[i]) + 'GeneralQuestionAnswers']
            if answer_generalquestion.strip != '':
                generalquestiontobeupdated = select(QuestionAnswers).where(QuestionAnswers.StudentNum == current_user.StudentNum, QuestionAnswers.ApplicationQuestionId == str(generalquestions_id[i]))
                generalquestionupdate = QuestionAnswers.query.filter_by(StudentNum=current_user.StudentNum, ApplicationQuestionId=str(generalquestions_id[i])).first()
                rowgeneral = db.session.execute(generalquestiontobeupdated)
                if rowgeneral and generalquestionupdate:
                    generalquestionupdate.Answer = answer_generalquestion
                    generalquestionupdate.Status = status
                    try:
                        db.session.commit()
                    except:
                        return redirect(url_for('get_application', ClubId=str(ClubId), StudentNum=current_user.StudentNum) + '?mode=view#nav-generalquestionanswers')
                else:
                    new_application_save = QuestionAnswers(QuestionAnswerId=generate_UUID(), StudentNum=current_user.StudentNum, ClubId=str(ClubId), Grade=current_user.Grade, Status=status, ApplicationQuestionId=generalquestions_id[i], Answer=answer_generalquestion)
                    db.session.add(new_application_save)
                    db.session.commit()
                    try:
                        db.session.commit()
                    except:
                        return redirect(url_for('get_application', ClubId=str(ClubId), StudentNum=current_user.StudentNum) + '?mode=view#nav-generalquestionanswers')
        for i in range(len(rolespecificquestions_to_display)):
            answer_rolespecificquestion = request.form[str(rolespecificquestions_id[i]) + 'RoleSpecificQuestionAnswers']
            roleid = ClubRoles.query.filter_by(RoleId=rolespecificquestions_id[i]).first()
            if answer_rolespecificquestion.strip != '':
                rolespecificquestiontobeupdated = select(QuestionAnswers).where(QuestionAnswers.StudentNum == current_user.StudentNum, QuestionAnswers.ApplicationQuestionId == str(rolespecificquestions_id[i]))
                rolespecificquestionupdate = QuestionAnswers.query.filter_by(StudentNum=current_user.StudentNum, ApplicationQuestionId=str(rolespecificquestions_id[i])).first()
                rowrolespecfic = db.session.execute(rolespecificquestiontobeupdated)
                if rowrolespecfic and rolespecificquestionupdate:
                    rolespecificquestionupdate.Answer = answer_rolespecificquestion
                    rolespecificquestionupdate.Status = status
                    try:
                        db.session.commit()
                    except:
                        return redirect(url_for('get_application', ClubId=str(ClubId), StudentNum=current_user.StudentNum) + '?mode=view#nav-generalquestionanswers')
                else:
                    new_application_save = QuestionAnswers(QuestionAnswerId=generate_UUID(), StudentNum=current_user.StudentNum, ClubId=str(ClubId), Grade=current_user.Grade, Status=status, RoleId=str(selectedrole_id), ApplicationQuestionId=rolespecificquestions_id[i], Answer=answer_rolespecificquestion)
                    db.session.add(new_application_save)
                    db.session.commit()
        return redirect(url_for('get_application', ClubId=str(ClubId), StudentNum=current_user.StudentNum) + '?mode=view#nav-generalquestionanswers')
    elif mode == 'selectrole':
        form = ClubApplicationForm()
        selectedrole_id = form.SelectRole.data
        selectedrole_str = ClubRoles.query.filter_by(RoleId=str(selectedrole_id)).first()
        selectedrole_str = selectedrole_str.Role
        generalquestions_to_display, generalquestions_ids = generalquestions(ClubId)
        role_options, role_descriptions, RoleIds = uniqueRoles(ClubId)
        length_role = len(role_options)
        length_general = len(generalquestions_to_display)
        rolespecificquestions_to_display, rolespecificquestions_ids = rolespecificquestions(str(selectedrole_id))
        print(rolespecificquestions_to_display)
        length_rolespecificquestions_to_display = len(rolespecificquestions_to_display)
        checkifsubmitted = QuestionAnswers.query.filter_by(StudentNum=StudentNum, Status='submitted')
        generalquestion_answers = QuestionAnswers.query.filter_by(StudentNum=StudentNum, RoleId=None)
        rolespecificquestion_answers = QuestionAnswers.query.filter_by(StudentNum=StudentNum, RoleId=str(selectedrole_id))
        rolespecificquestion_maxlengths = rolespecificquestion_maxlength(selectedrole_id)
        application_state, application_status_checked = '', ''
        selectroletabvisibility = ''
        for row in checkifsubmitted:
            if row.Status == 'submitted':
                application_state = 'disabled'
                application_status_checked = 'checked'
                selectroletabvisibility = 'visibility: hidden;'
            else:
                application_state = ''
                application_status_checked = ''
        all_generalquestion_answers = []
        all_rolespecificquestion_answers = []
        for row1 in generalquestion_answers:
            all_generalquestion_answers.append(row1.Answer)
        for row2 in rolespecificquestion_answers:
            all_rolespecificquestion_answers.append(row2.Answer)
        return redirect(url_for('get_application', ClubId=str(ClubId), StudentNum=current_user.StudentNum) + '?mode=view#nav-rolespecificquestionsanswers')
    
# Global variables
selectedrole_id = ''
selectedrole_str = ''