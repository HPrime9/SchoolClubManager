# Import libraries
from flask import render_template, redirect, url_for, request
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField
from wtforms.validators import InputRequired, Email, Length
from flask_login import login_required, current_user
from sqlalchemy import delete

# Import custom libraries
from clubmanager import app, db
from clubmanager.models import Club, ClubStudentMap, ApplicationQuestions, ClubRole, Announcement
from clubmanager.functions import generate_UUID, uniqueRoles, rolespecificquestions
from clubmanager.flaskforms import RoleSpecificQuestionForm

@app.route('/clubs/<uuid:ClubId>/roles/<uuid:RoleId>/rolespecificquestions', methods=['POST'])
@app.route('/clubs/<uuid:ClubId>/roles/<uuid:RoleId>/rolespecificquestions/<uuid:QuestionId>', methods=['POST'])
@login_required
def create_update_delete_rolespecificquestion(ClubId, RoleId, QuestionId = ''):
    mode = request.args.get('mode') 
    form = RoleSpecificQuestionForm()
    RoleSpecificQuestion = request.form.getlist('RoleSpecificQuestion')
    ResponseLength = request.form.getlist('LengthOfResponse')
    OrderNumber = request.form.getlist('RoleSpecificQuestionOrderNumber')
    if mode == 'new':
        if form.validate_on_submit:
            if len(RoleSpecificQuestion) >= 1:
                for i in range(len(RoleSpecificQuestion)):
                    if RoleSpecificQuestion[i].strip() != '' and ResponseLength[i].strip() != '' and OrderNumber[i].strip() != '':
                        new_rolespecificquestion = ApplicationQuestions(QuestionId=generate_UUID(), ClubId=str(ClubId), RoleId=str(RoleId), OrderNumber=OrderNumber[i], Question=RoleSpecificQuestion[i], LengthOfResponse=ResponseLength[i])
                        db.session.add(new_rolespecificquestion)
                        try:
                            db.session.commit()
                        except:
                            return 'there was problem adding role and question'
                roles, role_descriptions, RoleId = uniqueRoles(ClubId)
                length = len(roles)
                updClubInfo = Club.query.get_or_404(str(ClubId))  
                questions_to_display = ApplicationQuestions.query.filter(ApplicationQuestions.ClubId==str(ClubId)) 
                Announcements = Announcement.query.filter(Announcement.ClubId==str(ClubId)).all() 
                return render_template('updateclub.html', RoleId=RoleId, ClubId=str(ClubId), length=length, roles=roles, \
                role_descriptions=role_descriptions, Announcements=Announcements, length2 = 5, updClubInfo=updClubInfo,questions_to_display=questions_to_display)
    elif mode == 'update':
        updClubQuestions = ApplicationQuestions.query.get_or_404(str(QuestionId))   
        if form.validate_on_submit: 
            updClubQuestions.Question = request.form['RoleSpecificQuestion']
            updClubQuestions.LengthOfResponse = request.form['LengthOfResponse']
            updClubQuestions.OrderNumber = request.form['RoleSpecificQuestionOrderNumber']
            try:
                db.session.commit()
                roles, role_descriptions, RoleId = uniqueRoles(ClubId)
                length = len(roles)
                updClubInfo = Club.query.get_or_404(str(ClubId))  
                questions_to_display = ApplicationQuestions.query.filter(ApplicationQuestions.ClubId==str(ClubId)) 
                Announcements = Announcement.query.filter(Announcement.ClubId==str(ClubId)).all() 
                return render_template('updateclub.html', RoleId=RoleId, ClubId=str(ClubId), length=length, roles=roles, \
                role_descriptions=role_descriptions, Announcements=Announcements, length2 = 5, updClubInfo=updClubInfo,questions_to_display=questions_to_display)
            except:
                return 'there was problem updating'
    elif mode == 'delete':
        question_to_del = ApplicationQuestions.query.get_or_404(str(QuestionId))
        db.session.delete(question_to_del)
        db.session.commit()
        roles, role_descriptions, RoleId = uniqueRoles(ClubId)
        length = len(roles)
        updClubInfo = Club.query.get_or_404(str(ClubId))  
        questions_to_display = ApplicationQuestions.query.filter(ApplicationQuestions.ClubId==str(ClubId)) 
        Announcements = Announcement.query.filter(Announcement.ClubId==str(ClubId)).all() 
        return render_template('updateclub.html', RoleId=RoleId, ClubId=str(ClubId), length=length, roles=roles, \
        role_descriptions=role_descriptions, Announcements=Announcements, length2 = 5, updClubInfo=updClubInfo,questions_to_display=questions_to_display)
    else:
        return 'error'



