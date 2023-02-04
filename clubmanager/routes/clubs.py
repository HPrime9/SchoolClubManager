# Import libraries
from flask import render_template, redirect, url_for, request
from flask_login import login_required, current_user
from sqlalchemy import delete

# Import custom libraries
from clubmanager import app, db
from clubmanager.models import Club, ClubStudentMap, ApplicationQuestions, ClubRole, Announcement
from clubmanager.functions import generate_UUID, uniqueRoles, rolespecificquestions
from clubmanager.flaskforms import ClubCreationForm, ClubGeneralQuestionForm


# GET routes for creating a club and updating
@app.route('/clubs', methods=['GET'])
@app.route('/clubs/<uuid:ClubId>', methods=['GET'])
@login_required
def get_club(ClubId = ''):
    mode = request.args.get('mode')
    if mode == 'new':  
        return render_template('club.html')
    elif mode == 'update':
        roles, role_descriptions, RoleId = uniqueRoles(ClubId)
        length = len(roles)
        updClubInfo = Club.query.get_or_404(str(ClubId))  
        questions_to_display = ApplicationQuestions.query.filter(ApplicationQuestions.ClubId==str(ClubId)) 
        Announcements = Announcement.query.filter(Announcement.ClubId==str(ClubId)).all() 
        # info_to_display = ApplicationQuestions.query.filter(ApplicationQuestions.RoleId==str(RoleIdInUrl)) 
        # role_specific_questions_to_display, ids = rolespecificquestions(RoleIdInUrl) role_specific_questions_to_display=info_to_display
        # length2 = len(role_specific_questions_to_display) length2=length2
        return render_template('updateclub.html', RoleId=RoleId, ClubId=ClubId, length=length, roles=roles, \
            role_descriptions=role_descriptions, Announcements=Announcements, updClubInfo=updClubInfo,questions_to_display=questions_to_display)
    elif mode == 'viewall':
        clubs = Club.query.filter(Club.School == current_user.School).all()
        truthy = True
        if clubs:
            truthy = False
        return render_template('viewclubs.html', School=current_user.School, truthy=truthy, ClubCatalogue=clubs)
    elif mode == 'view':
        club_to_display = Club.query.get_or_404(str(ClubId))
        Announcements = Announcement.query.filter(Announcement.ClubId==str(ClubId)).all() 
        if club_to_display:
            return render_template('clubpage.html', club_to_display=club_to_display, Announcements=Announcements)
    else:
        return 'error'

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