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
from clubmanager.functions import generate_UUID, uniqueRoles, rolespecificquestions, generalquestions, getUserOwnedClubs, generalquestions_maxlength, rolespecificquestion_maxlength
from clubmanager.flaskforms import ClubApplicationForm

@app.route('/clubs/<uuid:ClubId>/applications', methods=['GET'])
@app.route('/clubs/<uuid:ClubId>/applications/<int:StudentNum>', methods=['GET'])
@login_required
def get_application(ClubId, StudentNum = ''):
    mode = request.args.get('mode')
    global selectedrole_str, selectedrole_id
    roles_to_display = []
    generalquestions_to_display = []
    club_to_display_responses = QuestionAnswer.query.filter(QuestionAnswer.ClubId == str(ClubId)).all()
    if mode == 'viewall':
        userClubCatalogue = getUserOwnedClubs(current_user.StudentNum)
        for row in club_to_display_responses:
            if row.Status != 'draft':
                name_role = ClubRole.query.filter(ClubRole.RoleId==str(row.RoleId)).first()
                try:
                    for row in name_role:
                        roles_to_display.append(row.Role)
                except:
                    print('error2')
        return render_template('responseoverview.html', userClubCatalogue=userClubCatalogue, club_to_display_responses=club_to_display_responses, roles_to_display=roles_to_display)
    elif mode == 'view' or mode == 'selectrole':
        checkapplicationstartdate = Club.query.filter_by(ClubId=str(ClubId)).first().AppStartDate
        if checkapplicationstartdate == datetime.now().date():
            form = ClubApplicationForm()
            generalquestions_to_display, generalquestions_ids = generalquestions(ClubId)
            role_options, role_descriptions, RoleIds = uniqueRoles(ClubId)
            length_role = len(role_options)
            length_general = len(generalquestions_to_display)
            rolespecificquestions_to_display, rolespecificquestions_ids = rolespecificquestions(str(selectedrole_id))
            length_rolespecificquestions_to_display = len(rolespecificquestions_to_display)
            checkifsubmitted = QuestionAnswer.query.filter_by(StudentNum=StudentNum, Status='submitted')
            generalquestion_answers = QuestionAnswer.query.filter_by(StudentNum=StudentNum, RoleId=None)
            rolespecificquestion_answers = QuestionAnswer.query.filter_by(StudentNum=StudentNum, RoleId=str(selectedrole_id))
            application_state, application_status_checked = '', ''
            selectroletabvisibility = ''
            all_generalquestion_answers = []
            all_rolespecificquestion_answers = []
            generalquestions_maxlengths = generalquestions_maxlength(ClubId)
            rolespecificquestion_maxlengths = rolespecificquestion_maxlength(selectedrole_id)
            for row1 in generalquestion_answers:
                all_generalquestion_answers.append(row1.Answer)
            for row2 in rolespecificquestion_answers:
                all_rolespecificquestion_answers.append(row2.Answer)
            for row in checkifsubmitted:
                if row.Status == 'submitted':
                    application_state = 'disabled'
                    application_status_checked = 'checked'
                    selectroletabvisibility = 'visibility: hidden;'
                else:
                    application_state = ''
                    application_status_checked = ''
            return render_template('application.html', rolespecificquestion_maxlengths=rolespecificquestion_maxlengths, generalquestions_maxlengths=generalquestions_maxlengths, selectroletabvisibility=selectroletabvisibility, form=form, all_rolespecificquestion_answers=all_rolespecificquestion_answers, all_generalquestion_answers=all_generalquestion_answers, ClubId=ClubId, rolespecificquestions_ids=rolespecificquestions_ids, length_rolespecificquestions_to_display=length_rolespecificquestions_to_display, rolespecificquestions_to_display=rolespecificquestions_to_display, application_status_checked=application_status_checked, application_state=application_state, RoleIds=RoleIds, selectedrole_str=selectedrole_str, generalquestions=generalquestions_to_display, length_general=length_general, generalquestions_ids=generalquestions_ids, length_role=length_role, role_options=role_options, role_descriptions=role_descriptions)
        else:
            return redirect(url_for('get_club', ClubId=str(ClubId)) + '?mode=view')






    #     class ClubApplicationForm(FlaskForm):
    # SubmitApplication = StringField('General Question Answer', validators=[Length(max=1000)])
    # GeneralQuestionAnswers = StringField('General Question Answer', validators=[InputRequired(), Length(max=1000)])
    # SelectRole = StringField('Select Role', validators=[InputRequired(), Length(max=500)])
    # RoleSpecificQuestionAnswers = StringField('Role Specific Question Answer', validators=[InputRequired(), Length(max=1000)])
    else:
        return 'error in application'

@app.route('/clubs/<uuid:ClubId>/applications/<int:StudentNum>', methods=['POST'])
@login_required
def save_submit_application(ClubId, StudentNum):
    mode = request.args.get('mode')
    global selectedrole_str, selectedrole_id
    if mode == 'save':
        form = ClubApplicationForm()
        if form.validate_on_submit:
            general_questions, generalquestions_id = generalquestions(ClubId)
            rolespecificquestions_to_display, rolespecificquestions_id = rolespecificquestions(str(selectedrole_id))
            if request.form.get('SubmitApplication') == 'submitapplication':
                status = 'submitted'
            else:
                status = 'draft'
            for i in range(len(general_questions)):
                answer_generalquestion = request.form[str(generalquestions_id[i]) + 'GeneralQuestionAnswers']
                if answer_generalquestion.strip != '':
                    generalquestiontobeupdated = select(QuestionAnswer).where(QuestionAnswer.StudentNum == current_user.StudentNum, QuestionAnswer.QuestionId == str(generalquestions_id[i]))
                    generalquestionupdate = QuestionAnswer.query.filter_by(StudentNum=current_user.StudentNum, QuestionId=str(generalquestions_id[i])).first()
                    rowgeneral = db.session.execute(generalquestiontobeupdated)
                    if rowgeneral and generalquestionupdate:
                        generalquestionupdate.Answer = answer_generalquestion
                        generalquestionupdate.Status = status
                        try:
                            db.session.commit()
                        except:
                            return 'error'
                    else:
                        new_application_save = QuestionAnswer(AnswerId=generate_UUID(), StudentNum=current_user.StudentNum, ClubId=str(ClubId), Grade=current_user.Grade, Status=status, QuestionId=generalquestions_id[i], Answer=answer_generalquestion)
                        db.session.add(new_application_save)
                        db.session.commit()
                        try:
                            db.session.commit()
                        except:
                            return 'there was problem updating'
            for i in range(len(rolespecificquestions_to_display)):
                answer_rolespecificquestion = request.form[str(rolespecificquestions_id[i]) + 'RoleSpecificQuestionAnswers']
                roleid = ClubRole.query.filter_by(RoleId=rolespecificquestions_id[i]).first()
                if answer_rolespecificquestion.strip != '':
                    rolespecificquestiontobeupdated = select(QuestionAnswer).where(QuestionAnswer.StudentNum == current_user.StudentNum, QuestionAnswer.QuestionId == str(rolespecificquestions_id[i]))
                    rolespecificquestionupdate = QuestionAnswer.query.filter_by(StudentNum=current_user.StudentNum, QuestionId=str(rolespecificquestions_id[i])).first()
                    rowrolespecfic = db.session.execute(rolespecificquestiontobeupdated)
                    if rowrolespecfic and rolespecificquestionupdate:
                        rolespecificquestionupdate.Answer = answer_rolespecificquestion
                        rolespecificquestionupdate.Status = status
                        try:
                            db.session.commit()
                        except:
                            return 'error'
                    else:
                        new_application_save = QuestionAnswer(AnswerId=generate_UUID(), StudentNum=current_user.StudentNum, ClubId=str(ClubId), Grade=current_user.Grade, Status=status, RoleId=str(selectedrole_id), QuestionId=rolespecificquestions_id[i], Answer=answer_rolespecificquestion)
                        db.session.add(new_application_save)
                        db.session.commit()
            return redirect(url_for('dashboard'))
    elif mode == 'selectrole':
        form = ClubApplicationForm()
        selectedrole_id = form.SelectRole.data
        selectedrole_str = ClubRole.query.filter_by(RoleId=str(selectedrole_id)).first()
        selectedrole_str = selectedrole_str.Role
        generalquestions_to_display, generalquestions_ids = generalquestions(ClubId)
        role_options, role_descriptions, RoleIds = uniqueRoles(ClubId)
        length_role = len(role_options)
        length_general = len(generalquestions_to_display)
        rolespecificquestions_to_display, rolespecificquestions_ids = rolespecificquestions(str(selectedrole_id))
        print(rolespecificquestions_to_display)
        length_rolespecificquestions_to_display = len(rolespecificquestions_to_display)
        checkifsubmitted = QuestionAnswer.query.filter_by(StudentNum=StudentNum, Status='submitted')
        generalquestion_answers = QuestionAnswer.query.filter_by(StudentNum=StudentNum, RoleId=None)
        rolespecificquestion_answers = QuestionAnswer.query.filter_by(StudentNum=StudentNum, RoleId=str(selectedrole_id))
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
        return render_template('application.html', selectroletabvisibility=selectroletabvisibility, form=form, all_rolespecificquestion_answers=all_rolespecificquestion_answers, all_generalquestion_answers=all_generalquestion_answers, ClubId=ClubId, rolespecificquestions_ids=rolespecificquestions_ids, length_rolespecificquestions_to_display=length_rolespecificquestions_to_display, rolespecificquestions_to_display=rolespecificquestions_to_display, application_status_checked=application_status_checked, application_state=application_state, RoleIds=RoleIds, selectedrole_str=selectedrole_str, generalquestions=generalquestions_to_display, length_general=length_general, generalquestions_ids=generalquestions_ids, length_role=length_role, role_options=role_options, role_descriptions=role_descriptions)

    else:
        return 'error'

# Global variables
selectedrole_id = ''
selectedrole_str = ''