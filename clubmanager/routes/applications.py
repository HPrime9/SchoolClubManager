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
from clubmanager.models import Clubs, ClubRoles, QuestionAnswers, Applications, ApplicationQuestions, ClubStudentMaps, Students
from clubmanager.functions import generate_UUID, uniqueRoles, rolespecificquestions, generalquestions, getUserOwnedClubs, generalquestions_maxlength, rolespecificquestion_maxlength
from clubmanager.flaskforms import ClubApplicationForm, ApplicationSelectForm

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
        all_club_applications = Applications.query.filter_by(ClubId=str(ClubId)).all()
        form = ApplicationSelectForm()
        # checkapplicationenddate = Clubs.query.filter_by(ClubId=str(ClubId)).first().AppEndDate
        # showsendresultsbttn = False
        # if datetime.now().date() > checkapplicationenddate:
        #     showsendresultsbttn = True
        # else:
        #     showsendresultsbttn = False  CHANGE THIS AFTER TO SHOW or not BUTTON
        showsendresultsbttn = True

        stmt = select(Applications.ApplicationId, Applications.RoleIdApplyingFor, Applications.EmailSent, Applications.ClubOwnerNotes, Students.id, Students.FirstName, \
            Students.LastName, Students.StudentNum, Students.Grade, \
            ClubRoles.Role)\
                .select_from(Applications)\
                .join(Students, Applications.StudentId == Students.id)\
                .join(ClubRoles, Applications.RoleIdApplyingFor == ClubRoles.RoleId) \
                .where(Applications.ApplicationState == 'submitted')
        data = db.session.execute(stmt)
        return render_template('responseoverview.html', data=data, showsendresultsbttn=showsendresultsbttn, form=form, userClubCatalogue=userClubCatalogue, ClubId=ClubId)
    elif mode == 'view' or mode == 'selectrole':
        if Applications.query.filter_by(StudentId=str(StudentId)).first() == None:
            selectedrole_id = ''
            selectedrole_str = ''
        else:
            selectedrole_id = Applications.query.filter_by(StudentId=str(StudentId)).first().RoleIdApplyingFor
            selectedrole_str = ClubRoles.query.filter_by(RoleId=str(selectedrole_id)).first()
            selectedrole_str = selectedrole_str.Role

        checkapplicationstartdate = Clubs.query.filter_by(ClubId=str(ClubId)).first().AppStartDate
        checkapplicationenddate = Clubs.query.filter_by(ClubId=str(ClubId)).first().AppEndDate
        
        query = ClubStudentMaps.query.filter_by(StudentId=str(current_user.id), ClubId=str(ClubId)).first()
        if query == None:
            query = None
        else:
            query = str(query.StudentId)

        condition = datetime.now().date() > checkapplicationenddate and str(current_user.id) == query

        if str(current_user.id) == str(StudentId) or condition:
            if datetime.now().date() >= checkapplicationstartdate and datetime.now().date() <= checkapplicationenddate:
                form = ClubApplicationForm()
                generalquestions_to_display, generalquestions_ids = generalquestions(ClubId)
                generalquestions_to_display_and_ids = ApplicationQuestions.query.filter_by(ClubId=str(ClubId), RoleId=None)
                role_options_descriptions_ids = ClubRoles.query.filter_by(ClubId=str(ClubId))
                rolespecificquestions_to_display_and_ids = ApplicationQuestions.query.filter_by(RoleId=str(selectedrole_id))
                length_general = len(generalquestions_to_display)
                rolespecificquestions_to_display, rolespecificquestions_ids = rolespecificquestions(str(selectedrole_id))
                length_rolespecificquestions_to_display = len(rolespecificquestions_to_display)

                all_generalquestion_answers = []
                for row in generalquestions_to_display_and_ids:
                    general_question_id = str(row.ApplicationQuestionId)
                    general_question_ans_query = QuestionAnswers.query.filter_by(StudentId=str(StudentId), ApplicationQuestionId=general_question_id).first()
                    if general_question_ans_query == None:
                        all_generalquestion_answers.append('')
                    else:
                        all_generalquestion_answers.append(general_question_ans_query.Answer)
                
                all_rolespecificquestion_answers = []
                for row in rolespecificquestions_to_display_and_ids:
                    rolespecificquestion_id = str(row.ApplicationQuestionId)
                    rolespecificquestion_ans_query = QuestionAnswers.query.filter_by(StudentId=str(StudentId), ApplicationQuestionId=rolespecificquestion_id).first()
                    if rolespecificquestion_ans_query == None:
                        all_rolespecificquestion_answers.append('')
                    else:
                        all_rolespecificquestion_answers.append(rolespecificquestion_ans_query.Answer)

                
                checkifsubmitted = Applications.query.filter_by(ClubId=str(ClubId), StudentId=str(StudentId), ApplicationState='submitted').first()
                rolespecificquestion_maxlengths = rolespecificquestion_maxlength(selectedrole_id)
                application_state = ''
                selectroletabvisibility = ''
                application_state_checked = ''
                if checkifsubmitted != None:
                    application_state = 'disabled'
                    application_state_checked = 'checked'
                    selectroletabvisibility = 'hidden'

                return render_template('application.html', application_state_checked=application_state_checked, all_rolespecificquestion_answers=all_rolespecificquestion_answers, StudentId=str(StudentId), form=form, selectedrole_str=selectedrole_str, role_options_descriptions_ids=role_options_descriptions_ids, ClubId=str(ClubId), rolespecificquestions_ids=rolespecificquestions_ids, rolespecificquestion_maxlengths=rolespecificquestion_maxlengths, rolespecificquestions_to_display=rolespecificquestions_to_display, length_rolespecificquestions_to_display=length_rolespecificquestions_to_display, SelectedRole=selectedrole_str, all_generalquestion_answers=all_generalquestion_answers, application_state=application_state, generalquestions_ids=generalquestions_ids, generalquestions_maxlengths=generalquestions_maxlengths, generalquestions=generalquestions_to_display, length_general=length_general)
    return redirect(url_for('get_club', ClubId=str(ClubId)) + '?mode=view')


@app.route('/clubs/<uuid:ClubId>/applications/<uuid:StudentId>', methods=['POST'])
@login_required
def save_submit_application(ClubId, StudentId):
    mode = request.args.get('mode')
    global selectedrole_str, selectedrole_id
    state_of_application = ''
    if mode == 'save':
        form = ClubApplicationForm()
        general_questions, generalquestions_id = generalquestions(ClubId)
        rolespecificquestions_to_display, rolespecificquestions_id = rolespecificquestions(str(selectedrole_id))
        if request.form.get('SubmitApplication') == 'submitapplication':
            state_of_application = 'submitted'
        else:
            state_of_application = 'draft'
        
        applicantexists = Applications.query.filter_by(ClubId=str(ClubId), StudentId=str(StudentId)).first()
        if applicantexists == None:
            new_application = Applications(ApplicationId=generate_UUID(), StudentId=str(StudentId), ClubId=str(ClubId), RoleIdApplyingFor=str(selectedrole_id), ApplicationState=state_of_application, EmailSent='No')
            db.session.add(new_application)
            try:
                db.session.commit()
            except:
                print()
        else:
            updApplicationInfo = applicantexists
            updApplicationInfo.RoleIdApplyingFor = str(selectedrole_id)
            updApplicationInfo.ApplicationState = state_of_application


        for i in range(len(general_questions)):
            answer_generalquestion = request.form[str(generalquestions_id[i]) + 'GeneralQuestionAnswers']
            if answer_generalquestion.strip != '':
                generalquestiontobeupdated = select(QuestionAnswers).where(QuestionAnswers.StudentId == current_user.id, QuestionAnswers.ApplicationQuestionId == str(generalquestions_id[i]))
                generalquestionupdate = QuestionAnswers.query.filter_by(StudentId=current_user.id, ApplicationQuestionId=str(generalquestions_id[i])).first()
                rowgeneral = db.session.execute(generalquestiontobeupdated)
                if rowgeneral and generalquestionupdate:
                    generalquestionupdate.Answer = answer_generalquestion
                    try:
                        db.session.commit()
                    except:
                        return redirect(url_for('get_application', ClubId=str(ClubId), StudentId=current_user.id) + '?mode=view#nav-generalquestionanswers')
                else:
                    new_application_save = QuestionAnswers(QuestionAnswerId=generate_UUID(), StudentId=current_user.id, ClubId=str(ClubId), ApplicationQuestionId=generalquestions_id[i], Answer=answer_generalquestion)
                    db.session.add(new_application_save)
                    try:
                        db.session.commit()
                    except:
                        return redirect(url_for('get_application', ClubId=str(ClubId), StudentId=current_user.id) + '?mode=view#nav-generalquestionanswers')
        for i in range(len(rolespecificquestions_to_display)):
            answer_rolespecificquestion = request.form[str(rolespecificquestions_id[i]) + 'RoleSpecificQuestionAnswers']
            roleid = ClubRoles.query.filter_by(RoleId=rolespecificquestions_id[i]).first()
            if answer_rolespecificquestion.strip != '':
                rolespecificquestiontobeupdated = select(QuestionAnswers).where(QuestionAnswers.StudentId == current_user.id, QuestionAnswers.ApplicationQuestionId == str(rolespecificquestions_id[i]))
                rolespecificquestionupdate = QuestionAnswers.query.filter_by(StudentId=current_user.id, ApplicationQuestionId=str(rolespecificquestions_id[i])).first()
                rowrolespecfic = db.session.execute(rolespecificquestiontobeupdated)
                if rowrolespecfic and rolespecificquestionupdate:
                    rolespecificquestionupdate.Answer = answer_rolespecificquestion
                    try:
                        db.session.commit()
                    except:
                        return redirect(url_for('get_application', ClubId=str(ClubId), StudentId=current_user.id) + '?mode=view#nav-generalquestionanswers')
                else:
                    new_application_save = QuestionAnswers(QuestionAnswerId=generate_UUID(), StudentId=current_user.id, ClubId=str(ClubId), RoleId=str(selectedrole_id), ApplicationQuestionId=rolespecificquestions_id[i], Answer=answer_rolespecificquestion)
                    db.session.add(new_application_save)
                    db.session.commit()
        return redirect(url_for('get_application', ClubId=str(ClubId), StudentId=current_user.id) + '?mode=view#nav-generalquestionanswers')
    elif mode == 'selectrole':
        form = ClubApplicationForm()
        selectedrole_id = form.SelectRole.data
        selectedrole_str = ClubRoles.query.filter_by(RoleId=str(selectedrole_id)).first()
        selectedrole_str = selectedrole_str.Role
        if Applications.query.filter_by(StudentId=str(StudentId)).first() == None:
            new_application = Applications(ApplicationId=generate_UUID(), StudentId=str(StudentId), ClubId=str(ClubId), RoleIdApplyingFor=str(selectedrole_id), EmailSent='No')
            db.session.add(new_application)
            try:
                db.session.commit()
            except:
                return redirect(url_for('get_application', ClubId=str(ClubId), StudentId=current_user.id) + '?mode=view#nav-generalquestionanswers')
        else:
            print(67)
            updApplicationInfo = Applications.query.filter_by(ClubId=str(ClubId), StudentId=str(StudentId)).first()
            print(selectedrole_id)
            print(updApplicationInfo.RoleIdApplyingFor)
            updApplicationInfo.RoleIdApplyingFor = str(selectedrole_id)
            try:
                db.session.commit()
            except:
                return redirect(url_for('get_application', ClubId=str(ClubId), StudentId=str(current_user.id)) + '?mode=view#nav-rolespecificquestionsanswers')
        return redirect(url_for('get_application', ClubId=str(ClubId), StudentId=str(current_user.id)) + '?mode=view#nav-rolespecificquestionsanswers')
    return redirect(url_for('get_club', ClubId=str(ClubId)) + '?mode=view')
    
# Global variables
selectedrole_id = ''
selectedrole_str = ''