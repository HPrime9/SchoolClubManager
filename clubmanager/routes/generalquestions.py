# Import libraries
from flask import render_template, redirect, url_for, request
from flask_login import login_required, current_user
from sqlalchemy import delete

# Import custom libraries
from clubmanager import app, db
from clubmanager.models import Club, ClubStudentMap, ApplicationQuestions, ClubRole, Announcement
from clubmanager.functions import generate_UUID, uniqueRoles, rolespecificquestions
from clubmanager.flaskforms import ClubGeneralQuestionForm


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
    updClubInfo = Club.query.get_or_404(str(ClubId))   
    questions_to_display = ApplicationQuestions.query.filter(ApplicationQuestions.ClubId==str(ClubId))
    updClubQuestions = ApplicationQuestions.query.get_or_404(str(QuestionId))   
    if mode == 'new':
        if form.validate_on_submit:
            for i in range(len(GeneralQuestions)):
                if GeneralQuestions[i].strip() != '' and GeneralQuestionsLengthOfResponse[i].strip() != '' and GeneralQuestionOrderNumbers[i].strip() != '':
                    new_general_question = ApplicationQuestions(QuestionId=generate_UUID(), ClubId=str(ClubId), Question=GeneralQuestions[i], LengthOfResponse=GeneralQuestionsLengthOfResponse[i], OrderNumber=GeneralQuestionOrderNumbers[i])
                    db.session.add(new_general_question)
                    try:
                        db.session.commit()
                    except:
                        return 'there was problem adding general question'
            return render_template('generalquestions.html', form=form, updClubInfo=updClubInfo, questions_to_display=questions_to_display)
        else:
            return 'invalid information'
    elif mode == 'update':
        if form.validate_on_submit: 
            updClubQuestions.Question = request.form['GeneralQuestions']
            updClubQuestions.LengthOfResponse = request.form['GeneralQuestionsLengthOfResponse']
            updClubQuestions.OrderNumber = request.form['GeneralQuestionOrderNumbers']
            try:
                db.session.commit()
                return render_template('generalquestions.html', form=form, updClubInfo=updClubInfo, questions_to_display=questions_to_display)
            except:
                return 'there was problem updating'
    elif mode == 'delete':
        question_to_del = ApplicationQuestions.query.get_or_404(str(QuestionId))
        db.session.delete(question_to_del)
        db.session.commit()
        return redirect(url_for('get_club', ClubId=ClubId))
    else:
        return 'error'