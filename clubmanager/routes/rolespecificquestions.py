# Import libraries
from flask import redirect, url_for, request
from flask_login import login_required

# Import custom libraries
from clubmanager import app, db
from clubmanager.models import ApplicationQuestions
from clubmanager.functions import generate_UUID

# Create routes
@app.route('/clubs/<uuid:ClubId>/roles/<uuid:RoleId>/rolespecificquestions', methods=['POST'])
@app.route('/clubs/<uuid:ClubId>/roles/<uuid:RoleId>/rolespecificquestions/<uuid:QuestionId>', methods=['POST'])
@login_required
def create_update_delete_rolespecificquestion(ClubId, RoleId, QuestionId = ''):
    # get mode
    mode = request.args.get('mode') 

    # get role specific questions and their details that the owner entered
    RoleSpecificQuestion = request.form.getlist('RoleSpecificQuestion')
    ResponseLength = request.form.getlist('LengthOfResponse')
    OrderNumber = request.form.getlist('RoleSpecificQuestionOrderNumber')

    # create new role specific questions 
    if mode == 'new':
        if len(RoleSpecificQuestion) >= 1:
            for i in range(len(RoleSpecificQuestion)):
                if RoleSpecificQuestion[i].strip() != '' and ResponseLength[i].strip() != '' and OrderNumber[i].strip() != '':
                    new_rolespecificquestion = ApplicationQuestions(ApplicationQuestionId=generate_UUID(), ClubId=str(ClubId), RoleId=str(RoleId), OrderNumber=OrderNumber[i], Question=RoleSpecificQuestion[i], LengthOfResponse=ResponseLength[i])
                    db.session.add(new_rolespecificquestion)
                    try:
                        db.session.commit()
                    except:
                        return redirect(url_for('get_club', ClubId=str(ClubId)) + '?mode=update#nav-rolespecificquestions' + str(RoleId))

    # update role specific question
    elif mode == 'update':
        updClubQuestions = ApplicationQuestions.query.get_or_404(str(QuestionId))   
        updClubQuestions.Question = request.form['RoleSpecificQuestion']
        updClubQuestions.LengthOfResponse = request.form['LengthOfResponse']
        updClubQuestions.OrderNumber = request.form['RoleSpecificQuestionOrderNumber']
        try:
            db.session.commit()
        except:
            return redirect(url_for('get_club', ClubId=str(ClubId)) + '?mode=update#nav-rolespecificquestions' + str(RoleId))
    
    # delete role specific question
    elif mode == 'delete':
        question_to_del = ApplicationQuestions.query.get_or_404(str(QuestionId))
        db.session.delete(question_to_del)
        try:
            db.session.commit()
        except:
            return redirect(url_for('get_club', ClubId=str(ClubId)) + '?mode=update#nav-rolespecificquestions' + str(RoleId))
    
    # load the role specific question page the user is on
    return redirect(url_for('get_club', ClubId=str(ClubId)) + '?mode=update#nav-rolespecificquestions' + str(RoleId))