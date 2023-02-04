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


@app.route('/clubs/<uuid:ClubId>/announcements', methods=['POST'])
@app.route('/clubs/<uuid:ClubId>/announcements/<uuid:AnnouncementId>', methods=['POST'])
@login_required
def club_announcement(ClubId):
    mode = request.args.get('mode')
    form = AnnouncementForm()
    if mode == 'new':
        if form.validate_on_submit: 
            new_announcemnt = Announcement(AnnouncementId=generate_UUID(), ClubId=str(ClubId), Header=form.Header.data, Message=form.Message.data)
            db.session.add(new_announcemnt)
            try:
                db.session.commit()
                return redirect(url_for('get_club', ClubId=ClubId))
            except:
                return 'there was problem making announcement'
    elif mode == 'delete':
        announcement_to_del = Announcement.query.get_or_404(str(AnnouncementId))
        db.session.delete(announcement_to_del)
        db.session.commit()
        return redirect(url_for('get_club', ClubId=ClubId))
    else:
        return 'not valid update not created yet'