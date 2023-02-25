# Import libraries
from flask import render_template, request, url_for, redirect
from flask_login import login_required, current_user
from sqlalchemy import select
from datetime import datetime

# import custom models
from clubmanager import app, db
from clubmanager.models import Clubs, ClubRoles, QuestionAnswers, Applications, ApplicationQuestions, ClubStudentMaps, Students
from clubmanager.functions import generate_UUID, uniqueRoles, rolespecificquestions, generalquestions, getUserOwnedClubs, generalquestions_maxlength, rolespecificquestion_maxlength
from clubmanager.flaskforms import ClubApplicationForm, ApplicationSelectForm

# Create app routes

@app.route('/clubs/<uuid:ClubId>/applications', methods=['GET'])
@app.route('/clubs/<uuid:ClubId>/applications/<uuid:StudentId>', methods=['GET'])
@login_required
def get_application(ClubId, StudentId = ''):
    # get mode
    mode = request.args.get('mode')

    # call on global variables that give user's selected role name and id
    global selectedrole_str, selectedrole_id

    # get the information needed to display the general questions
    generalquestions_to_display = []
    generalquestions_maxlengths = generalquestions_maxlength(ClubId) 
    if mode == 'viewall':
        # get user owned clubs to show on response page
        userClubCatalogue = getUserOwnedClubs(current_user.id)

        # initialize form
        form = ApplicationSelectForm()

        # COMMENTED TO SHOW FEATURES AS IF TURNED ON THE SUBMIT RESULTS BUTTON WOULD ONLY SHOW UP WHEN APPLICATION DATE IS OVER
        # checkapplicationenddate = Clubs.query.filter_by(ClubId=str(ClubId)).first().AppEndDate
        # showsendresultsbttn = False
        # if datetime.now().date() > checkapplicationenddate:
        #     showsendresultsbttn = True
        # else:
        #     showsendresultsbttn = False  CHANGE THIS AFTER TO SHOW or not BUTTON
        showsendresultsbttn = True

        # get unique applicants
        stmt = select(Applications.ApplicationId, Applications.RoleIdApplyingFor, Applications.RoleIdSelectedFor, Applications.EmailSent, Applications.ClubOwnerNotes, Students.id, Students.FirstName, \
            Students.LastName, Students.StudentNum, Students.Email, Students.Grade, \
            ClubRoles.Role)\
                .select_from(Applications)\
                .join(Students, Applications.StudentId == Students.id)\
                .join(ClubRoles, Applications.RoleIdApplyingFor == ClubRoles.RoleId) \
                .where(Applications.ApplicationState == 'submitted', Applications.ClubId == str(ClubId))
        data = db.session.execute(stmt)
        ClubName_to_display = Clubs.query.filter_by(ClubId=str(ClubId)).first().ClubName

        # render the page
        return render_template('responseoverview.html', ClubName_to_display=ClubName_to_display, data=data, showsendresultsbttn=showsendresultsbttn, form=form, userClubCatalogue=userClubCatalogue, ClubId=ClubId)
    elif mode == 'view' or mode == 'selectrole':
        # get the role and id
        if Applications.query.filter_by(ClubId=str(ClubId), StudentId=str(StudentId)).first() == None:
            selectedrole_id = ''
            selectedrole_str = ''
        else:
            selectedrole_id = Applications.query.filter_by(ClubId=str(ClubId), StudentId=str(StudentId)).first().RoleIdApplyingFor
            selectedrole_str = ClubRoles.query.filter_by(RoleId=str(selectedrole_id)).first()
            selectedrole_str = selectedrole_str.Role

        checkapplicationstartdate = Clubs.query.filter_by(ClubId=str(ClubId)).first().AppStartDate
        checkapplicationenddate = Clubs.query.filter_by(ClubId=str(ClubId)).first().AppEndDate
        
        # part of creating the condition
        query = ClubStudentMaps.query.filter_by(StudentId=str(current_user.id), ClubId=str(ClubId)).first()
        if query == None:
            query = None
        else:
            query = str(query.StudentId)

        condition = datetime.now().date() > checkapplicationenddate and str(current_user.id) == query

        # if condition is true then applicant application is visible as only applicants can see their own application and club owners can see it only after the application deadline
        if str(current_user.id) == str(StudentId) or condition:
            if datetime.now().date() >= checkapplicationstartdate and datetime.now().date() <= checkapplicationenddate:

                # get the information needed to display the application
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

                # if everyting is already submitted then prevent anyone from editing the application
                if checkifsubmitted != None:
                    application_state = 'disabled'
                    application_state_checked = 'checked'
                    selectroletabvisibility = 'hidden'

                # render the page
                return render_template('application.html', application_state_checked=application_state_checked, all_rolespecificquestion_answers=all_rolespecificquestion_answers, StudentId=str(StudentId), form=form, selectedrole_str=selectedrole_str, role_options_descriptions_ids=role_options_descriptions_ids, ClubId=str(ClubId), rolespecificquestions_ids=rolespecificquestions_ids, rolespecificquestion_maxlengths=rolespecificquestion_maxlengths, rolespecificquestions_to_display=rolespecificquestions_to_display, length_rolespecificquestions_to_display=length_rolespecificquestions_to_display, SelectedRole=selectedrole_str, all_generalquestion_answers=all_generalquestion_answers, application_state=application_state, generalquestions_ids=generalquestions_ids, generalquestions_maxlengths=generalquestions_maxlengths, generalquestions=generalquestions_to_display, length_general=length_general)
    return redirect(url_for('get_club', ClubId=str(ClubId)) + '?mode=view')


@app.route('/clubs/<uuid:ClubId>/applications/<uuid:StudentId>', methods=['POST'])
@login_required
def save_submit_application(ClubId, StudentId):
    # get the mode
    mode = request.args.get('mode')

    # call on global variables to get the role name and id
    global selectedrole_str, selectedrole_id

    # initialize local variables
    state_of_application = ''

    # if mode is save then save the application in the database correspondingly as if they are a returning applicant then the database
    # should update instead of creating a new row
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
        if Applications.query.filter_by(ClubId=str(ClubId), StudentId=str(StudentId)).first() == None:
            new_application = Applications(ApplicationId=generate_UUID(), StudentId=str(StudentId), ClubId=str(ClubId), RoleIdApplyingFor=str(selectedrole_id), EmailSent='No')
            db.session.add(new_application)
            try:
                db.session.commit()
            except:
                return redirect(url_for('get_application', ClubId=str(ClubId), StudentId=current_user.id) + '?mode=view#nav-generalquestionanswers')
        else:
            updApplicationInfo = Applications.query.filter_by(ClubId=str(ClubId), StudentId=str(StudentId)).first()

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