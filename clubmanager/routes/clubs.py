# Import libraries
from flask import render_template, redirect, url_for, request
from flask_login import login_required, current_user
from sqlalchemy import delete
from datetime import datetime

# Import custom libraries
from clubmanager import app, db
from clubmanager.models import Club, ClubStudentMap, ApplicationQuestions, ClubRole, Announcement
from clubmanager.functions import generate_UUID, uniqueRoles, rolespecificquestions, validate_club_creation
from clubmanager.flaskforms import ClubCreationForm, ClubGeneralQuestionForm, ClubRoleForm


# GET routes for creating a club and updating
@app.route('/clubs', methods=['GET'])
@app.route('/clubs/<uuid:ClubId>', methods=['GET'])
@login_required
def get_club(ClubId = ''):
    mode = request.args.get('mode')
    formClubCreationForm = ClubCreationForm()
    if mode == 'new':  
        errors_in_clubcreation = ['', '']
        return render_template('club.html', formClubCreationForm=formClubCreationForm, errors_in_clubcreation=errors_in_clubcreation)
    elif mode == 'update':
        errors_in_clubcreation = ['', '']
        roles, role_descriptions, RoleId = uniqueRoles(ClubId)
        length = len(roles)
        updClubInfo = Club.query.get_or_404(str(ClubId))  
        questions_to_display = ApplicationQuestions.query.filter(ApplicationQuestions.ClubId==str(ClubId)) 
        Announcements = Announcement.query.filter(Announcement.ClubId==str(ClubId)).all() 
        # info_to_display = ApplicationQuestions.query.filter(ApplicationQuestions.RoleId==str(RoleIdInUrl)) 
        # role_specific_questions_to_display, ids = rolespecificquestions(RoleIdInUrl) role_specific_questions_to_display=info_to_display
        return render_template('updateclub.html', formClubCreationForm=formClubCreationForm, RoleId=RoleId, ClubId=str(ClubId), length=length, roles=roles, \
            role_descriptions=role_descriptions, errors_in_clubcreation=errors_in_clubcreation, Announcements=Announcements, updClubInfo=updClubInfo,questions_to_display=questions_to_display)
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
            return render_template('clubpage.html', StudentNumUrl=int(current_user.StudentNum), club_to_display=club_to_display, Announcements=Announcements)
    else:
        return 'errerer'

# POST routes for creating, updating and deleting a club
@app.route('/clubs', methods=['POST'])
@app.route('/clubs/<uuid:ClubId>', methods=['POST'])
@login_required
def create_update_delete_club(ClubId = ''):
    mode = request.args.get('mode')  
    formClubCreationForm = ClubCreationForm()
    errors_in_clubcreation = ['', '']
    if mode == 'new': 
        errors_in_clubcreation, condition_1_for_date, condition_2_for_date, condition_3_for_email = validate_club_creation(formClubCreationForm)
        if formClubCreationForm.validate_on_submit():
            if condition_1_for_date and condition_2_for_date and condition_3_for_email:
                dummy_id = generate_UUID()
                new_club = Club(ClubId=dummy_id, StudentNum=current_user.StudentNum, School=current_user.School, ClubName=formClubCreationForm.ClubName.data, ClubDescription=formClubCreationForm.ClubDescription.data, AppStartDate=formClubCreationForm.AppStartDate.data, AppEndDate=formClubCreationForm.AppEndDate.data, ClubContactEmail=formClubCreationForm.ClubContactEmail.data)
                new_clubstudentmap = ClubStudentMap(ClubStudentMapId=generate_UUID(), StudentId = current_user.id, ClubId=dummy_id)
                db.session.add(new_club)
                db.session.add(new_clubstudentmap)
                db.session.commit()
                return redirect(url_for('dashboard'))
        return render_template('club.html', formClubCreationForm=formClubCreationForm, errors_in_clubcreation=errors_in_clubcreation)
    elif mode == 'update':
        updClubInfo = Club.query.get_or_404(str(ClubId))
        roles, role_descriptions, rolesId = uniqueRoles(ClubId)
        errors_in_clubcreation, condition_1_for_date, condition_2_for_date, unusedvariable = validate_club_creation(formClubCreationForm)
        condition_3_for_email = False
        getclubemail = Club.query.filter_by(ClubId=str(ClubId)).first()
        checkifemailunique = Club.query.filter_by(ClubContactEmail=str(formClubCreationForm.ClubContactEmail.data)).first()
        if str(formClubCreationForm.ClubContactEmail.data) == str(getclubemail.ClubContactEmail) or checkifemailunique == None:
            condition_3_for_email = True
        else:
            errors_in_clubcreation[1] = ''

        if formClubCreationForm.validate_on_submit: 
            if condition_1_for_date and condition_2_for_date and condition_3_for_email:
                updClubInfo.ClubName = request.formClubCreationForm['ClubName']
                updClubInfo.ClubDescription = request.formClubCreationForm['ClubDescription']
                updClubInfo.AppStartDate = request.formClubCreationForm['AppStartDate']
                updClubInfo.AppEndDate = request.formClubCreationForm['AppEndDate']
                updClubInfo.ClubContactEmail = request.formClubCreationForm['ClubContactEmail']
                db.session.commit()
                roles, role_descriptions, rolesId = uniqueRoles(ClubId)
        return render_template('updateclub.html', formClubCreationForm=formClubCreationForm, updClubInfo=updClubInfo, errors_in_clubcreation=errors_in_clubcreation, RoleId=rolesId, rolesId=rolesId, roles=roles, length=len(roles))
    elif mode == 'delete':
        club_to_del = Club.query.get_or_404(str(ClubId))
        club_to_del_from_cs_map = ClubStudentMap.query.filter_by(ClubId=str(ClubId)).first()
        db.session.delete(club_to_del)
        db.session.delete(club_to_del_from_cs_map)
        db.session.commit()
        return redirect(url_for('dashboard'))