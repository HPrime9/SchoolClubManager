# Import libraries
from flask import redirect, url_for, request, flash
from flask_login import login_required

# Import custom libraries
from clubmanager import app, db
from clubmanager.models import ApplicationQuestions
from clubmanager.functions import generate_UUID
from clubmanager.flaskforms import ClubGeneralQuestionForm, ClubCreationForm

# Create app routes
@app.route('/clubs/<uuid:ClubId>/generalquestions', methods=['POST'])
@app.route('/clubs/<uuid:ClubId>/generalquestions/<uuid:QuestionId>', methods=['POST'])
@login_required
def create_update_delete_generalquestions(ClubId = '', QuestionId=''):
    # Get mode in the url
    mode = request.args.get('mode') 

    # get general questions that are created
    GeneralQuestions = request.form.getlist('GeneralQuestions')
    GeneralQuestionsLengthOfResponse = request.form.getlist('GeneralQuestionsLengthOfResponse')
    GeneralQuestionOrderNumbers = request.form.getlist('GeneralQuestionOrderNumbers')

    # create a new entry in the table if a new general question is being created
    if mode == 'new':
        for i in range(len(GeneralQuestions)):
            if GeneralQuestions[i].strip() != '' and GeneralQuestionsLengthOfResponse[i].strip() != '' and GeneralQuestionOrderNumbers[i].strip() != '':
                new_general_question = ApplicationQuestions(ApplicationQuestionId=generate_UUID(), ClubId=str(ClubId), Question=GeneralQuestions[i], LengthOfResponse=GeneralQuestionsLengthOfResponse[i], OrderNumber=GeneralQuestionOrderNumbers[i])
                db.session.add(new_general_question)
                try:
                    db.session.commit()
                except:
                    return redirect(url_for('get_club', ClubId=str(ClubId)) + '?mode=update#nav-generalquestions')

    # update the already existing entry in the table if a general question is being updated
    elif mode == 'update':
        updClubQuestions = ApplicationQuestions.query.get_or_404(str(QuestionId))    
        updClubQuestions.Question = request.form['GeneralQuestions']
        updClubQuestions.LengthOfResponse = request.form['GeneralQuestionsLengthOfResponse']
        updClubQuestions.OrderNumber = request.form['GeneralQuestionOrderNumbers']
        try:
            db.session.commit()
        except:
            return redirect(url_for('get_club', ClubId=str(ClubId)) + '?mode=update#nav-generalquestions')
    
    # delete the already existing entry in the table if a general question is being deleted
    elif mode == 'delete':
        question_to_del = ApplicationQuestions.query.filter_by(ApplicationQuestionId=str(QuestionId)).first()
        db.session.delete(question_to_del)
        try:
            db.session.commit()
        except:
            return redirect(url_for('get_club', ClubId=str(ClubId)) + '?mode=update#nav-generalquestions')
    # load the same page again
    return redirect(url_for('get_club', ClubId=str(ClubId)) + '?mode=update#nav-generalquestions')