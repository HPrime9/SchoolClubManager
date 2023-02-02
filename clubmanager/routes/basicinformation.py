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

# Create a class containing basic information required to start a club
class ClubCreationForm(FlaskForm):
    ClubName = StringField('Club Name', validators=[InputRequired(), Length(min=2, max=50)])
    ClubDescription = StringField('Club Description', validators=[InputRequired(), Length(max=300)])
    AppStartDate = StringField('Application Start Date', validators=[InputRequired(), Length(min=5, max=35)])
    AppEndDate = StringField('Application End Date', validators=[InputRequired(), Length(min=5, max=35)])
    ClubContactEmail = StringField('Club Contact Email', validators=[InputRequired(), Email(message='Invalid Email'), Length(max=55)])

# GET routes for creating a club and updating
@app.route('/clubs', methods=['GET'])
@app.route('/clubs/<uuid:ClubId>', methods=['GET'])
@login_required
def get_club(ClubId = ''):
    mode = request.args.get('mode')
    form = ClubCreationForm()
    if mode == 'new':  
        return render_template('club.html', form=form)
    elif mode == 'update':
        updClubInfo = Club.query.get_or_404(str(ClubId))   
        roles, role_descriptions, rolesId = uniqueRoles(ClubId)
        return render_template('updateclub.html', form=form, updClubInfo=updClubInfo, rolesId=rolesId, roles=roles, length=len(roles))

# POST routes for creating, updating and deleting a club
@app.route('/clubs', methods=['POST'])
@app.route('/clubs/<uuid:ClubId>', methods=['POST'])
@login_required
def create_update_delete_club(ClubId = ''):
    mode = request.args.get('mode')  
    form = ClubCreationForm()
    if mode == 'new': 
        if form.validate_on_submit():
            dummy_id = generate_UUID()
            new_club = Club(ClubId=dummy_id, StudentNum=current_user.StudentNum, School=current_user.School, ClubName=form.ClubName.data, ClubDescription=form.ClubDescription.data, AppStartDate=form.AppStartDate.data, AppEndDate=form.AppEndDate.data, ClubContactEmail=form.ClubContactEmail.data)
            new_clubstudentmap = ClubStudentMap(ClubStudentMapId=generate_UUID(), StudentId = current_user.id, ClubId=dummy_id)
            db.session.add(new_club)
            db.session.add(new_clubstudentmap)
            db.session.commit()
            return redirect(url_for('dashboard'))
    elif mode == 'update':
        updClubInfo = Club.query.get_or_404(str(ClubId))
        roles, role_descriptions, rolesId = uniqueRoles(ClubId)
        if form.validate_on_submit: 
            updClubInfo.ClubName = request.form['ClubName']
            updClubInfo.ClubDescription = request.form['ClubDescription']
            updClubInfo.AppStartDate = request.form['AppStartDate']
            updClubInfo.AppEndDate = request.form['AppEndDate']
            updClubInfo.ClubContactEmail = request.form['ClubContactEmail']
            db.session.commit()
            roles, role_descriptions, rolesId = uniqueRoles(ClubId)
            return render_template('updateclub.html', form=form, updClubInfo=updClubInfo, rolesId=rolesId, roles=roles, length=len(roles))
    elif mode == 'delete':
        club_to_del = Club.query.get_or_404(str(ClubId))
        club_to_del_from_cs_map = ClubStudentMap.query.filter_by(ClubId=str(ClubId)).first()
        db.session.delete(club_to_del)
        db.session.delete(club_to_del_from_cs_map)
        db.session.commit()
        return redirect(url_for('dashboard'))