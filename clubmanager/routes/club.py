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
from clubmanager.flaskforms import ClubCreationForm, ClubGeneralQuestionForm, ClubRoleForm, RoleSpecificQuestionForm, AnnouncementForm


@app.route('/club/<uuid:ClubId>/<uuid:RoleId>/rolespecificquestions', methods=['GET', 'POST'])
@login_required
def create_rolespecificquestion(ClubId, RoleId):
    form = RoleSpecificQuestionForm()
    role_specific_questions_to_display, ids = rolespecificquestions(RoleId)
    info_to_display = ApplicationQuestions.query.filter(ApplicationQuestions.RoleId==str(RoleId))
    RoleSpecificQuestion = request.form.getlist('RoleSpecificQuestion')
    ResponseLength = request.form.getlist('LengthOfResponse')
    OrderNumber = request.form.getlist('RoleSpecificQuestionOrderNumber')
    length = len(role_specific_questions_to_display)
    if form.validate_on_submit:
        if request.method == 'POST' and len(RoleSpecificQuestion) >= 1:
            for i in range(len(RoleSpecificQuestion)):
                if RoleSpecificQuestion[i].strip() != '' and ResponseLength[i].strip() != '' and OrderNumber[i].strip() != '':
                    new_rolespecificquestion = ApplicationQuestions(QuestionId=generate_UUID(), ClubId=str(ClubId), RoleId=str(RoleId), OrderNumber=OrderNumber[i], Question=RoleSpecificQuestion[i], LengthOfResponse=ResponseLength[i])
                    db.session.add(new_rolespecificquestion)
                    try:
                        db.session.commit()
                    except:
                        return 'there was problem adding role and question'
            return redirect(url_for('update_club', Id=ClubId))
        else:
            return render_template('rolespecificquestions.html', form=form, length=length, RoleId=RoleId, ClubId=ClubId, role_specific_questions_to_display=info_to_display)
    else:
        return 'invalid information'





@app.route('/update/<uuid:QuestionId>/rolespecificquestion', methods=['GET', 'POST'])
@login_required
def update_rolespecificquestionquestion(QuestionId):
    form = RoleSpecificQuestionForm()
    updClubQuestions = ApplicationQuestions.query.get_or_404(str(QuestionId))   
    if form.validate_on_submit: 
        if request.method == 'POST':
            updClubQuestions.Question = request.form['RoleSpecificQuestion']
            updClubQuestions.LengthOfResponse = request.form['LengthOfResponse']
            updClubQuestions.OrderNumber = request.form['RoleSpecificQuestionOrderNumber']
            try:
                db.session.commit()
                return redirect(url_for('update_club', Id=updClubQuestions.ClubId))
            except:
                return 'there was problem updating'
        else:
            return 'WRONG METHOD'
    else:
        return 'not valid information'
      




@app.route('/club/<uuid:Id>')
def club_page(Id):
    club_to_display = Club.query.get_or_404(str(Id))
    Announcements = Announcement.query.filter(Announcement.ClubId==str(Id)).all() 
    if club_to_display:
        return render_template('clubpage.html', club_to_display=club_to_display, Announcements=Announcements)
    else:
        return 'Club does not exist'


@app.route('/announce/<uuid:ClubId>', methods=['GET', 'POST'])
@login_required
def club_announcement(ClubId):
    form = AnnouncementForm()
    if form.validate_on_submit: 
        if request.method == 'POST':
            new_announcemnt = Announcement(AnnouncementId=generate_UUID(), ClubId=str(ClubId), Header=form.Header.data, Message=form.Message.data)
            db.session.add(new_announcemnt)
            try:
                db.session.commit()
                return redirect(url_for('dashboard'))
            except:
                return 'there was problem making announcement'
        else:
            return render_template('announce.html', form=form, ClubId=ClubId)
    else:
        return 'not valid'

# @app.route('/announce/<uuid:ClubId>', methods=['POST'])
# @login_required
# def club_announcement(ClubId):
#     form = AnnouncementForm()
#     if form.validate_on_submit:
#         new_announcemnt = Announcement(AnnouncementId=generate_UUID(), ClubId=ClubId, Header=form.Header.data, Message=form.Message.data)
#         db.session.add(new_announcemnt)
#         db.session.commit()
#         return redirect(url_for('dashboard'))

@app.route('/viewclubs')
@login_required
def viewclubs():
    clubs = Club.query.filter(Club.School == current_user.School).all()
    truthy = True
    if clubs:
        truthy = False
    return render_template('viewclubs.html', School=current_user.School, truthy=truthy, ClubCatalogue=clubs)