# Import libraries
from flask import render_template, redirect, url_for, request
from flask_login import login_required, current_user
from sqlalchemy import delete
from datetime import datetime

# Import custom libraries
from clubmanager import app, db
from clubmanager.models import Clubs, ClubStudentMaps, ApplicationQuestions, ClubRoles, Announcements
from clubmanager.functions import generate_UUID, uniqueRoles, rolespecificquestions, validate_club_creation
from clubmanager.flaskforms import ClubCreationForm, ClubGeneralQuestionForm, ClubRoleForm, AnnouncementForm


# GET routes for creating a club and updating
@app.route('/clubs', methods=['GET'])
@app.route('/clubs/<uuid:ClubId>', methods=['GET'])
@login_required
def get_club(ClubId = ''):
    # initialize variables
    mode = request.args.get('mode')
    formClubCreationForm = ClubCreationForm()
    formCreateGeneralQuestions = ClubGeneralQuestionForm()
    formAnnouncement = AnnouncementForm()

    # if mode is new then just render the create a club page
    if mode == 'new':  
        errors_in_clubcreation = ['', '']
        return render_template('club.html', formClubCreationForm=formClubCreationForm, errors_in_clubcreation=errors_in_clubcreation)
    
    # if mode is update then render the previously filled information and the update.html page
    elif mode == 'update':
        errors_in_clubcreation = ['', '']
        all_role_specific_questions_to_display = []
        roles, role_descriptions, RoleId = uniqueRoles(ClubId)
        for i in range(len(RoleId)):
            db_query_application_questions = ApplicationQuestions.query.filter(ApplicationQuestions.RoleId==str(RoleId[i])).all()
            all_role_specific_questions_to_display.append(db_query_application_questions)
        length = len(roles)
        updClubInfo = Clubs.query.get_or_404(str(ClubId))  
        questions_to_display = ApplicationQuestions.query.filter(ApplicationQuestions.ClubId==str(ClubId), ApplicationQuestions.RoleId==None).all()
        if questions_to_display:
            print(True)
        else:
            print(False)
        Announcements_var = Announcements.query.filter(Announcements.ClubId==str(ClubId)).all() 
        return render_template('updateclub.html', formAnnouncement=formAnnouncement, formCreateGeneralQuestions=formCreateGeneralQuestions, formClubCreationForm=formClubCreationForm, RoleId=RoleId, ClubId=str(ClubId), length=length, roles=roles, \
            role_descriptions=role_descriptions, errors_in_clubcreation=errors_in_clubcreation, all_role_specific_questions_to_display=all_role_specific_questions_to_display, Announcements=Announcements_var, updClubInfo=updClubInfo,questions_to_display=questions_to_display)
    
    # if mode is viewall then show all the clubs at the school
    elif mode == 'viewall':
        clubs = Clubs.query.filter(Clubs.School == current_user.School).all()
        truthy = True
        if clubs:
            truthy = False
        return render_template('viewclubs.html', School=current_user.School, truthy=truthy, ClubCatalogue=clubs)

    # if mode is view then show the club page and the announcements
    elif mode == 'view':
        club_to_display = Clubs.query.get_or_404(str(ClubId))
        Announcements_var = Announcements.query.filter(Announcements.ClubId==str(ClubId)).all() 
        checkapplicationstartdate = Clubs.query.filter_by(ClubId=str(ClubId)).first().AppStartDate
        checkapplicationenddate = Clubs.query.filter_by(ClubId=str(ClubId)).first().AppEndDate
        applicationbttnstate = 'disabled'
        applicationstatetext = ''
        if datetime.now().date() >= checkapplicationstartdate and datetime.now().date() <= checkapplicationenddate:
            applicationbttnstate = ''
            applicationstatetext = 'Applications Open! Apply Now!'
        else:
            checkapplicationstartdate = 'disabled'
            applicationstatetext = 'Applications are closed!'
        if club_to_display:
            return render_template('clubpage.html', StudentId=str(current_user.id), applicationstatetext=applicationstatetext, applicationbttnstate=applicationbttnstate, club_to_display=club_to_display, Announcements=Announcements_var)
    else:
        return redirect(url_for('dashboard'))

# POST routes for creating, updating and deleting a club
@app.route('/clubs', methods=['POST'])
@app.route('/clubs/<uuid:ClubId>', methods=['POST'])
@login_required
def create_update_delete_club(ClubId = ''):
    mode = request.args.get('mode')  
    form = ClubCreationForm()
    errors_in_clubcreation = ['', '']

    # if the mode is new then add the new club to the database after the information entered is valid
    if mode == 'new': 
        errors_in_clubcreation, condition_1_for_date, condition_2_for_date, condition_3_for_email = validate_club_creation(form)
        if form.validate_on_submit():
            if condition_1_for_date and condition_2_for_date and condition_3_for_email:
                dummy_id = generate_UUID()
                new_club = Clubs(ClubId=dummy_id, StudentId=current_user.id, School=current_user.School, ClubName=form.ClubName.data, ClubDescription=form.ClubDescription.data, AppStartDate=form.AppStartDate.data, AppEndDate=form.AppEndDate.data, ClubContactEmail=form.ClubContactEmail.data)
                new_clubstudentmap = ClubStudentMaps(ClubStudentMapId=generate_UUID(), StudentId = current_user.id, ClubId=dummy_id)
                db.session.add(new_club)
                db.session.add(new_clubstudentmap)
                try:
                    db.session.commit()
                except:
                    return redirect(url_for('dashboard'))
                return redirect(url_for('dashboard'))
        return render_template('club.html', formClubCreationForm=form, errors_in_clubcreation=errors_in_clubcreation)
    
    # if the mode is update then update the club's information
    elif mode == 'update':
        updClubInfo = Clubs.query.get_or_404(str(ClubId))
        clubappstartdate = Clubs.query.filter_by(ClubId=str(ClubId)).first().AppStartDate
        clubappenddate = Clubs.query.filter_by(ClubId=str(ClubId)).first().AppEndDate
        newappstartdate = form.AppStartDate.data
        newappenddate = form.AppEndDate.data
        errors_in_clubcreation, condition_1_for_date, condition_2_for_date, condition_3_for_email = validate_club_creation(form)
        condition_3_for_date, condition_4_for_date = str(newappstartdate) == str(clubappstartdate), str(newappenddate) == str(clubappenddate)
        condition_5_for_email = False
        emailuserupdatingto = form.ClubContactEmail.data
        getclubemail = Clubs.query.filter_by(ClubId=str(ClubId)).first()
        checkifemailunique = Clubs.query.filter_by(ClubContactEmail=emailuserupdatingto).first()
        if emailuserupdatingto == getclubemail.ClubContactEmail or checkifemailunique == None:
            condition_5_for_email = True
            errors_in_clubcreation[1] = ''
        else:
            errors_in_clubcreation[1] = 'Email Already Exists'
        if condition_3_for_date and condition_4_for_date:
            errors_in_clubcreation[0] = ''
        if form.validate_on_submit(): 
            if condition_5_for_email:
                if (condition_3_for_date and condition_4_for_date) or (condition_1_for_date and condition_2_for_date):
                    updClubInfo.ClubName = request.form['ClubName']
                    updClubInfo.ClubDescription = request.form['ClubDescription']
                    updClubInfo.AppStartDate = datetime.strptime(request.form['AppStartDate'], '%Y-%m-%d') 
                    updClubInfo.AppEndDate = datetime.strptime(request.form['AppEndDate'], '%Y-%m-%d')  
                    updClubInfo.ClubContactEmail = request.form['ClubContactEmail']
                    try:
                        db.session.commit()
                    except:
                        return redirect(url_for('get_club', ClubId=str(ClubId)) + '?mode=update#nav-generaldetails')
        return redirect(url_for('get_club', ClubId=str(ClubId)) + '?mode=update#nav-generaldetails')
    
    # if the mode is delete then delete the club from the database
    elif mode == 'delete':
        club_to_del = Clubs.query.get_or_404(str(ClubId))
        club_to_del_from_cs_map = ClubStudentMaps.query.filter_by(ClubId=str(ClubId)).first()
        db.session.delete(club_to_del)
        db.session.delete(club_to_del_from_cs_map)
        try:
            db.session.commit()
        except:
            return redirect(url_for('dashboard'))
        return redirect(url_for('dashboard'))
    else:
        return redirect(url_for('dashboard'))
