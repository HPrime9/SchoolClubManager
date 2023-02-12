# Import libraries
from flask import redirect, url_for, request
from flask_login import login_required

# Import custom libraries
from clubmanager import app, db
from clubmanager.models import Announcements
from clubmanager.functions import generate_UUID
from clubmanager.flaskforms import AnnouncementForm

# Create routes
@app.route('/clubs/<uuid:ClubId>/announcements', methods=['POST'])
@app.route('/clubs/<uuid:ClubId>/announcements/<uuid:AnnouncementId>', methods=['POST'])
@login_required
def club_announcement(ClubId, AnnouncementId = ''):
    # get mode
    mode = request.args.get('mode')

    # initialize form
    form = AnnouncementForm()

    # create a new announcement
    if mode == 'new':
        new_announcement = Announcements(AnnouncementId=generate_UUID(), ClubId=str(ClubId), Header=form.Header.data, Message=form.Message.data)
        db.session.add(new_announcement)
        try:
            db.session.commit()
        except:
            return redirect(url_for('get_club', ClubId=str(ClubId)) + '?mode=update#nav-announcements')
    
    # delete announcement
    elif mode == 'delete':
        announcement_to_del = Announcements.query.filter_by(AnnouncementId=str(AnnouncementId)).first()
        db.session.delete(announcement_to_del)
        try:
            db.session.commit()
        except:
            return redirect(url_for('get_club', ClubId=str(ClubId)) + '?mode=update#nav-announcements')
    
    # load same page
    return redirect(url_for('get_club', ClubId=str(ClubId)) + '?mode=update#nav-announcements')