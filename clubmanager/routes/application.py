# Import libraries
from flask import render_template, request, url_for, redirect
from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import InputRequired, Length
from flask_login import login_required, current_user
from sqlalchemy import select

# import custom models
from clubmanager import app, db
from clubmanager.models import ClubRole, QuestionAnswer
from clubmanager.functions import generate_UUID, uniqueRoles, rolespecificquestions, generalquestions, getUserOwnedClubs
from clubmanager.flaskforms import ClubApplicationForm

@app.route('/clubs/<uuid:ClubId>/applications', methods=['GET'])
@app.route('/clubs/<uuid:ClubId>/applications/<int:StudentNum>', methods=['GET'])
@login_required
def get_application(ClubId, StudentNum = ''):
    mode = request.args.get('mode')
    roles_to_display = []
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
        global selectedrole_id
        form = ClubApplicationForm()
        role_options, role_descriptions, RoleId = uniqueRoles(ClubId)
        general_questions, generalquestions_id = generalquestions(ClubId)
        length_role = len(role_options)
        selectedrole_id = form.SelectRole.data
        length_general = len(general_questions)
        rolespecificquestions_to_display = []
        length_rolespecificquestions_to_display = 0
        applicant_role = ''
        general_question_answers = []
        role_specific_question_answers = []
        generalanswers = QuestionAnswer.query.filter(QuestionAnswer.ClubId==str(ClubId))
        check_application_state = QuestionAnswer.query.filter(QuestionAnswer.StudentNum==int(current_user.StudentNum)).all()
        application_state = ''
        application_status_checked = ''
        rolespecificquestions_id = ''
        for row in check_application_state:
            if row.Status == 'submitted':
                application_state = 'disabled'
                application_status_checked = 'checked'
        for row in generalanswers:
            if not row.RoleId:
                general_question_answers.append(row.Answer)

            roleexists = select(QuestionAnswer).where(QuestionAnswer.StudentNum == current_user.StudentNum, QuestionAnswer.RoleId!=None)
            getroleidexists = QuestionAnswer.query.filter(QuestionAnswer.StudentNum==current_user.StudentNum, QuestionAnswer.RoleId!=None).first()
            roleexistsexecute = db.session.execute(roleexists)
            if getroleidexists and roleexistsexecute and not selectedrole_id:
                selectedrole_id = str(getroleidexists.RoleId)
                rolespecificanswers = QuestionAnswer.query.filter(QuestionAnswer.RoleId==str(selectedrole_id))
                for row2 in rolespecificanswers:
                    role_specific_question_answers.append(row2.Answer)
            else:
                row = ClubRole.query.filter(ClubRole.RoleId==str(selectedrole_id)).first()
                rolespecificanswers = QuestionAnswer.query.filter(QuestionAnswer.RoleId==str(selectedrole_id))
                for row2 in rolespecificanswers:
                    role_specific_question_answers.append(row2.Answer)
                try:
                    applicant_role = row.Role
                except:
                    print('error')
                rolespecificquestions_to_display, rolespecificquestions_id = rolespecificquestions(str(selectedrole_id))
                length_rolespecificquestions_to_display = len(rolespecificquestions_to_display)
        
        return render_template('application.html', RoleId=RoleId, application_status_checked=application_status_checked, \
            generalquestions_id=generalquestions_id, application_state=application_state, role_specific_question_answers=role_specific_question_answers, \
                general_question_answers=general_question_answers, rolespecificquestions_id=rolespecificquestions_id, form=form, \
                    length_rolespecificquestions_to_display=length_rolespecificquestions_to_display, \
                        rolespecificquestions_to_display=rolespecificquestions_to_display, length_general=length_general, length_role=length_role, \
                            SelectedRole=applicant_role, ClubId=str(ClubId), role_options=role_options, role_descriptions=role_descriptions, \
                                generalquestions=general_questions)
    else:
        return 'error in application'


@app.route('/clubs/<uuid:ClubId>/applications', methods=['POST'])
@login_required
def save_submit_application(ClubId):
    mode = request.args.get('mode')
    if mode == 'save':
        global selectedrole_id
        form = ClubApplicationForm()
        if form.validate_on_submit:
            if request.method == 'POST':
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
    else:
        return 'error'

# Global variables
selectedrole_id = ''