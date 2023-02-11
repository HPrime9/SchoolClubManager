# Import libraries
from flask import render_template, redirect, url_for, request
from flask_login import login_required, current_user
from sqlalchemy import delete

# Import custom libraries
from clubmanager import app, db
from clubmanager.models import Club, ClubStudentMap, ApplicationQuestions, ClubRole, Announcement
from clubmanager.functions import generate_UUID, uniqueRoles, rolespecificquestions
from clubmanager.flaskforms import ClubGeneralQuestionForm, ClubCreationForm


############################## url is not found when creating new question why?
@app.route('/clubs/<uuid:ClubId>/generalquestions', methods=['POST'])
@app.route('/clubs/<uuid:ClubId>/generalquestions/<uuid:QuestionId>', methods=['POST'])
@login_required
def create_update_delete_generalquestions(ClubId = '', QuestionId=''):
    mode = request.args.get('mode') 
    form = ClubGeneralQuestionForm()
    GeneralQuestions = request.form.getlist('GeneralQuestions')
    GeneralQuestionsLengthOfResponse = request.form.getlist('GeneralQuestionsLengthOfResponse')
    GeneralQuestionOrderNumbers = request.form.getlist('GeneralQuestionOrderNumbers')
    formClubCreationForm = ClubCreationForm()
    updClubInfo = Club.query.get_or_404(str(ClubId))  
    errors_in_clubcreation= ['', ''] 
    questions_to_display = ApplicationQuestions.query.filter(ApplicationQuestions.ClubId==str(ClubId))
    if mode == 'new':
        if form.validate_on_submit():
            for i in range(len(GeneralQuestions)):
                if GeneralQuestions[i].strip() != '' and GeneralQuestionsLengthOfResponse[i].strip() != '' and GeneralQuestionOrderNumbers[i].strip() != '':
                    new_general_question = ApplicationQuestions(QuestionId=generate_UUID(), ClubId=str(ClubId), Question=GeneralQuestions[i], LengthOfResponse=GeneralQuestionsLengthOfResponse[i], OrderNumber=GeneralQuestionOrderNumbers[i])
                    db.session.add(new_general_question)
                    try:
                        db.session.commit()
                    except:
                        return 'there was problem adding general question'
            roles, role_descriptions, RoleId = uniqueRoles(ClubId)
            length = len(roles)
            questions_to_display = ApplicationQuestions.query.filter(ApplicationQuestions.ClubId==str(ClubId)) 
            Announcements = Announcement.query.filter(Announcement.ClubId==str(ClubId)).all() 
            return redirect(url_for('get_club', ClubId=str(ClubId)) + '?mode=update#nav-generalquestions')
            # return render_template('updateclub.html', RoleId=RoleId, ClubId=str(ClubId), length=length, roles=roles, \
            # role_descriptions=role_descriptions, Announcements=Announcements, length2 = 5, updClubInfo=updClubInfo,questions_to_display=questions_to_display)
        else:
            return redirect(url_for('get_club', ClubId=str(ClubId)) + '?mode=update#nav-generalquestions')
    elif mode == 'update':
        if form.validate_on_submit:
            updClubQuestions = ApplicationQuestions.query.get_or_404(str(QuestionId))    
            updClubQuestions.Question = request.form['GeneralQuestions']
            updClubQuestions.LengthOfResponse = request.form['GeneralQuestionsLengthOfResponse']
            updClubQuestions.OrderNumber = request.form['GeneralQuestionOrderNumbers']
            try:
                db.session.commit()
                roles, role_descriptions, RoleId = uniqueRoles(ClubId)
                length = len(roles)
                updClubInfo = Club.query.get_or_404(str(ClubId))  
                questions_to_display = ApplicationQuestions.query.filter(ApplicationQuestions.ClubId==str(ClubId)) 
                Announcements = Announcement.query.filter(Announcement.ClubId==str(ClubId)).all() 
                return render_template('updateclub.html', formClubCreationForm=formClubCreationForm, RoleId=RoleId, ClubId=str(ClubId), length=length, roles=roles, \
                role_descriptions=role_descriptions, Announcements=Announcements, errors_in_clubcreation=errors_in_clubcreation, updClubInfo=updClubInfo,questions_to_display=questions_to_display)
            except:
                return 'there was problem updating'
    elif mode == 'delete':
        question_to_del = ApplicationQuestions.query.filter_by(QuestionId=str(QuestionId)).first()
        db.session.delete(question_to_del)
        db.session.commit()
        roles, role_descriptions, RoleId = uniqueRoles(ClubId)
        length = len(roles)
        updClubInfo = Club.query.get_or_404(str(ClubId))  
        questions_to_display = ApplicationQuestions.query.filter(ApplicationQuestions.ClubId==str(ClubId)) 
        Announcements = Announcement.query.filter(Announcement.ClubId==str(ClubId)).all() 
        return render_template('updateclub.html', formClubCreationForm=formClubCreationForm, RoleId=RoleId, ClubId=str(ClubId), length=length, roles=roles, \
        role_descriptions=role_descriptions, Announcements=Announcements, errors_in_clubcreation=errors_in_clubcreation, updClubInfo=updClubInfo,questions_to_display=questions_to_display)
    else:
        return 'error'