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