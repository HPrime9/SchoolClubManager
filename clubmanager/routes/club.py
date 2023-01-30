# Import libraries
from flask import render_template, redirect, url_for, request
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField
from wtforms.validators import InputRequired, Email, Length
from flask_login import login_required, current_user
from sqlalchemy import delete

# import custom models
from clubmanager import app, db
from clubmanager.models import Club, ClubStudentMap, ApplicationQuestions, ClubRole, Announcement
from clubmanager.functions import generate_UUID, uniqueRoles, rolespecificquestions

# Create a club create form
class ClubCreationForm(FlaskForm):
    ClubName = StringField('Club Name', validators=[InputRequired(), Length(min=2, max=50)])
    ClubDescription = StringField('Club Description', validators=[InputRequired(), Length(max=300)])
    AppStartDate = StringField('Application Start Date', validators=[InputRequired(), Length(min=5, max=35)])
    AppEndDate = StringField('Application End Date', validators=[InputRequired(), Length(min=5, max=35)])
    ClubContactEmail = StringField('Club Contact Email', validators=[InputRequired(), Email(message='Invalid Email'), Length(max=55)])
    
class ClubGeneralQuestionForm(FlaskForm):
    GeneralQuestions = StringField('General Questions', validators=[Length(max=1000)])
    GeneralQuestionsLengthOfResponse = IntegerField('Length Of Response')
    GeneralQuestionOrderNumbers = IntegerField('Question Order')

class ClubRoleForm(FlaskForm):
    Role = StringField('Roles', validators=[Length(max=500)])
    RoleDescription = StringField('Role Descriptions', validators=[Length(max=1000)])

class RoleSpecificQuestionForm(FlaskForm):
    RoleSpecificQuestion = StringField('Role Specific Questions', validators=[Length(max=1000)])
    LengthOfResponse = IntegerField('Length Of Response')
    RoleSpecificQuestionOrderNumber = IntegerField('Question Order')

# Create announcement form
class AnnouncementForm(FlaskForm):
    Header = StringField('Title', validators=[InputRequired(), Length(max=100)])
    Message = StringField('Write a Message', validators=[InputRequired(), Length(max=2000)])

@app.route('/club/basicinformation', methods=['GET'])
@login_required
def get_club():    
    form = ClubCreationForm()
    return render_template('club.html', form=form)

@app.route('/club/basicinformation', methods=['POST'])
@login_required
def create_club():    
    form = ClubCreationForm()
    if form.validate_on_submit():
        dummy_id = generate_UUID()
        new_club = Club(ClubId=dummy_id, StudentNum=current_user.StudentNum, School=current_user.School, ClubName=form.ClubName.data, ClubDescription=form.ClubDescription.data, AppStartDate=form.AppStartDate.data, AppEndDate=form.AppEndDate.data, ClubContactEmail=form.ClubContactEmail.data)
        new_clubstudentmap = ClubStudentMap(ClubStudentMapId=generate_UUID(), StudentId = current_user.id, ClubId=dummy_id)
        db.session.add(new_club)
        db.session.add(new_clubstudentmap)
        db.session.commit()
        return redirect(url_for('dashboard'))
    else:
        return 'invalid'
    
@app.route('/club/<uuid:ClubId>/generalquestions', methods=['GET', 'POST'])
@login_required
def create_generalquestion(ClubId):
    form = ClubGeneralQuestionForm()
    updClubInfo = Club.query.get_or_404(str(ClubId))   
    questions_to_display = ApplicationQuestions.query.filter(ApplicationQuestions.ClubId==str(ClubId))
    GeneralQuestions = request.form.getlist('GeneralQuestions')
    GeneralQuestionsLengthOfResponse = request.form.getlist('GeneralQuestionsLengthOfResponse')
    GeneralQuestionOrderNumbers = request.form.getlist('GeneralQuestionOrderNumbers')
    if form.validate_on_submit:
        if request.method == 'POST':
            for i in range(len(GeneralQuestions)):
                if GeneralQuestions[i].strip() != '' and GeneralQuestionsLengthOfResponse[i].strip() != '' and GeneralQuestionOrderNumbers[i].strip() != '':
                    new_general_question = ApplicationQuestions(QuestionId=generate_UUID(), ClubId=str(ClubId), Question=GeneralQuestions[i], LengthOfResponse=GeneralQuestionsLengthOfResponse[i], OrderNumber=GeneralQuestionOrderNumbers[i])
                    db.session.add(new_general_question)
                    try:
                        db.session.commit()
                    except:
                        return 'there was problem adding general question'
            return redirect(url_for('update_club', Id=ClubId))
        else:
            return render_template('generalquestions.html', form=form, updClubInfo=updClubInfo, questions_to_display=questions_to_display)
    else:
        return 'invalid information'

@app.route('/club/<uuid:ClubId>/clubroles', methods=['GET', 'POST'])
@login_required
def create_role(ClubId):
    form = ClubRoleForm()
    updClubInfo = Club.query.get_or_404(str(ClubId))   
    roles, role_descriptions, RoleId = uniqueRoles(ClubId)
    length = len(roles)
    Role = request.form.getlist('Role')
    RoleDescription = request.form.getlist('RoleDescription')
    if form.validate_on_submit:
        if request.method == 'POST':
            for i in range(len(Role)):
                if Role[i].strip() != '' and RoleDescription[i].strip() != '':
                    roleid = generate_UUID()
                    new_role_and_description = ClubRole(RoleId=roleid, ClubId=str(ClubId), Role=Role[i], RoleDescription=RoleDescription[i]) 
                    db.session.add(new_role_and_description)
                    try:
                        db.session.commit()
                    except:
                        return 'there was problem adding role and description'
            return redirect(url_for('update_club', Id=ClubId))
        else:
            return render_template('roles.html', form=form, RoleId=RoleId, ClubId=ClubId, length=length, updClubInfo=updClubInfo, roles=roles, role_descriptions=role_descriptions)
    else:
        return 'invalid information'

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

@app.route('/update/<uuid:Id>', methods=['GET', 'POST'])
@login_required
def update_club(Id):
    form = ClubCreationForm()
    updClubInfo = Club.query.get_or_404(str(Id))   
    roles, role_descriptions, rolesId = uniqueRoles(Id)
    if form.validate_on_submit: 
        if request.method == 'POST':
            updClubInfo.ClubName = request.form['ClubName']
            updClubInfo.ClubDescription = request.form['ClubDescription']
            updClubInfo.AppStartDate = request.form['AppStartDate']
            updClubInfo.AppEndDate = request.form['AppEndDate']
            updClubInfo.ClubContactEmail = request.form['ClubContactEmail']
            try:
                db.session.commit()
                return redirect(url_for('dashboard'))
            except:
                return 'there was problem updating'
        else:
            return render_template('updateclub.html', form=form, updClubInfo=updClubInfo, rolesId=rolesId, roles=roles, length=len(roles))
    else:
        return 'not vlaid'



@app.route('/update/<uuid:QuestionId>/generalquestion', methods=['POST'])
@login_required
def update_generalquestion(QuestionId):
    form = ClubGeneralQuestionForm()
    updClubQuestions = ApplicationQuestions.query.get_or_404(str(QuestionId))   
    if form.validate_on_submit: 
        if request.method == 'POST':
            updClubQuestions.Question = request.form['GeneralQuestions']
            updClubQuestions.LengthOfResponse = request.form['GeneralQuestionsLengthOfResponse']
            updClubQuestions.OrderNumber = request.form['GeneralQuestionOrderNumbers']
            try:
                db.session.commit()
                return redirect(url_for('update_club', Id=updClubQuestions.ClubId))
            except:
                return 'there was problem updating'
        else:
            return 'WRONG METHOD'
    else:
        return 'not valid information'


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

@app.route('/update/role/<uuid:ClubId>/<uuid:RoleId>', methods=['POST'])
def update_clubrole(ClubId, RoleId):
    form = ClubRoleForm()
    updClubRole = ClubRole.query.get_or_404(str(RoleId))
    if form.validate_on_submit: 
        if request.method == 'POST':
            if request.form['Role'].strip() != '' and request.form['RoleDescription'].strip() != '':
                updClubRole.Role = request.form['Role']
                updClubRole.RoleDescription = request.form['RoleDescription']
                try:
                    db.session.commit()
                    return redirect(url_for('update_club', Id=ClubId))
                except:
                    return 'there was problem updating'
        else:
            return 'WRONG METHOD'
    else:
        return 'not valid information'      

# @app.route('/delete/role/<uuid:ClubId>/<uuid:RoleId>')
@app.route('/club/<uuid:ClubId>/role/<uuid:RoleId>')
def delete_clubrole(ClubId, RoleId):
    # stmt = select(ApplicationQuestions).where(ApplicationQuestions.ClubId == str(ClubId), ApplicationQuestions.Role == Role)
    # print(stmt)
    # rows = db.session.execute(stmt)
    # for row in rows:
    #     print(row)

    delete_rows = delete(ApplicationQuestions).where(ApplicationQuestions.RoleId == str(RoleId))
    role_to_del = ClubRole.query.filter_by(RoleId=str(RoleId)).first()

    try:
        db.session.delete(role_to_del)
        db.session.commit()
        rows = db.session.execute(delete_rows)
        print(rows)
        return redirect(url_for('update_club', Id=ClubId))
    except:
        return 'sorry could not delete'

@app.route('/delete/<uuid:Id>')
def delete_club(Id):
    club_to_del = Club.query.get_or_404(str(Id))
    club_to_del_from_cs_map = ClubStudentMap.query.filter_by(ClubId=str(Id)).first()
    try:
        db.session.delete(club_to_del)
        db.session.delete(club_to_del_from_cs_map)
        db.session.commit()
        return redirect(url_for('dashboard'))
    except:
        return redirect(url_for('dashboard'))

@app.route('/delete/<uuid:ClubId>/<uuid:QuestionId>')
def delete_question(ClubId, QuestionId):
    question_to_del = ApplicationQuestions.query.get_or_404(str(QuestionId))
    try:
        db.session.delete(question_to_del)
        db.session.commit()
        return redirect(url_for('update_club', Id=ClubId))
    except:
        return 'sorry could not delete'


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