# Import libraries
from flask import render_template, request, url_for, redirect
from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import InputRequired, Length
from flask_login import login_required, current_user


# import custom models
from clubmanager import app, db
from clubmanager.models import ClubRole, QuestionAnswer
from clubmanager.functions import generate_UUID, uniqueRoles, rolespecificquestions, generalquestions

class ClubApplicationForm(FlaskForm):
    SubmitApplication = StringField('General Question Answer', validators=[Length(max=1000)])
    GeneralQuestionAnswers = StringField('General Question Answer', validators=[InputRequired(), Length(max=1000)])
    SelectRole = StringField('Select Role', validators=[InputRequired(), Length(max=500)])
    RoleSpecificQuestionAnswers = StringField('Role Specific Question Answer', validators=[InputRequired(), Length(max=1000)])

@app.route('/application/<uuid:ClubId>', methods=['GET', 'POST'])
@login_required
def club_application(ClubId):
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
    check_application_state = QuestionAnswer.query.filter(QuestionAnswer.StudentNum==str(current_user.StudentNum)).all()
    application_state = ''
    application_status_checked = ''
    for row in check_application_state:
        if row.Status == 'submitted':
            application_state = 'disabled'
            application_status_checked = 'checked'
    for row in generalanswers:
        if not row.RoleId:
            general_question_answers.append(row.Answer)
    if selectedrole_id != 'None':
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
    return render_template('application.html', RoleId=RoleId, application_status_checked=application_status_checked, generalquestions_id=generalquestions_id, application_state=application_state, role_specific_question_answers=role_specific_question_answers, general_question_answers=general_question_answers, rolespecificquestions_id=rolespecificquestions_id, form=form, length_rolespecificquestions_to_display=length_rolespecificquestions_to_display, rolespecificquestions_to_display=rolespecificquestions_to_display, length_general=length_general, length_role=length_role, SelectedRole=applicant_role, ClubId=ClubId, role_options=role_options, role_descriptions=role_descriptions, generalquestions=general_questions)


@app.route('/application/<uuid:ClubId>/save', methods=['POST'])
@login_required
def club_application_save(ClubId):
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
                    checkifinfoneedstobeupdated = QuestionAnswer.query.filter(QuestionAnswer.StudentNum == current_user.StudentNum)
                    for row in checkifinfoneedstobeupdated:
                        if row.QuestionId == str(generalquestions_id[i]):
                            print('update')
                    new_application_save = QuestionAnswer(AnswerId=generate_UUID(), StudentNum=current_user.StudentNum, ClubId=str(ClubId), Grade=current_user.Grade, Status=status, QuestionId=generalquestions_id[i], Answer=answer_generalquestion)
                    db.session.add(new_application_save)
                    db.session.commit()
            for i in range(len(rolespecificquestions_to_display)):
                answer_rolespecificquestion = request.form[str(rolespecificquestions_id[i]) + 'RoleSpecificQuestionAnswers']
                roleid = ClubRole.query.filter_by(RoleId=rolespecificquestions_id[i]).first()
                if answer_rolespecificquestion.strip != '':
                    new_application_save = QuestionAnswer(AnswerId=generate_UUID(), StudentNum=current_user.StudentNum, ClubId=str(ClubId), Grade=current_user.Grade, Status=status, RoleId=str(selectedrole_id), QuestionId=rolespecificquestions_id[i], Answer=answer_rolespecificquestion)
                    db.session.add(new_application_save)
                    db.session.commit()
            return redirect(url_for('my_clubs'))

@app.route('/responseoverview/<uuid:ClubId>')
@login_required
def response(ClubId):
    roles_to_display = []
    club_to_display_responses = QuestionAnswer.query.filter(QuestionAnswer.ClubId == str(ClubId)).all()
    for row in club_to_display_responses:
        name_role = ClubRole.query.filter(ClubRole.RoleId==row.RoleId)
        try:
            for row in name_role:
                roles_to_display.append(row.Role)
        except:
            print('error2')
    return render_template('responseoverview.html', club_to_display_responses=club_to_display_responses, roles_to_display=roles_to_display)

selectedrole_id = ''