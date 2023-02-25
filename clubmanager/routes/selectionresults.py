# Import libraries
from flask import request, url_for, redirect
from flask_login import login_required
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

# import custom models
from clubmanager import app, db
from clubmanager.models import Applications, ClubRoles, Clubs
from clubmanager.flaskforms import ApplicationSelectForm

@app.route('/clubs/<uuid:ClubId>/selectionresults', methods=['POST'])
@login_required
def sendresults(ClubId):
    
    # initialize variables
    form = ApplicationSelectForm()
    mode = request.args.get('mode')

    # check if mode is sendall and save all the information on the response page
    if mode == 'sendall':
        sendemaillist = []
        AllApplicationIds = request.form.getlist('ApplicationId')
        RoleIdsSelectedFor = request.form.getlist('RoleIdSelectedFor')
        AllClubOwnerNotes = request.form.getlist('ClubOwnerNotes')
        AllApplicantEmails = request.form.getlist('ApplicantEmail')
        for i in range(len(AllApplicationIds)):
            unique_applicant = Applications.query.filter_by(ApplicationId=str(AllApplicationIds[i])).first()
            unique_applicant.ClubOwnerNotes = AllClubOwnerNotes[i]
            if str(RoleIdsSelectedFor[i]) == 'None':
                unique_applicant.RoleIdSelectedFor = 'None'
                unique_applicant.EmailSent = 'No'
            else:
                unique_applicant.RoleIdSelectedFor = str(RoleIdsSelectedFor[i])
                if unique_applicant.EmailSent == 'No':
                    sendemaillist.append(AllApplicantEmails[i])
                    unique_applicant.EmailSent = 'Yes'
            try:
                db.session.commit()
            except:
                return redirect(url_for('get_application', ClubId=str(ClubId)) + '?mode=viewall')
            
        # Set email message for users that are in the club
        for i in range(len(sendemaillist)):
            RoleNameSelectedFor = ClubRoles.query.filter_by(RoleId=str(RoleIdsSelectedFor[i])).first().Role
            ClubNameInEmail = Clubs.query.filter_by(ClubId=str(ClubId)).first().ClubName
            ClubEmail_sender = Clubs.query.filter_by(ClubId=str(ClubId)).first().ClubContactEmail
            congratulations_message = Mail(from_email=ClubEmail_sender, to_emails=sendemaillist[i], subject='Congratulations you have been selected as a ' + RoleNameSelectedFor + ' in ' + ClubNameInEmail + '.', plain_text_content='Future Link here', html_content='<strong>CONGRATS!!</strong>' )
            try:
                sg = SendGridAPIClient(os.environ['SENDGRID_API_KEY'])
                response = sg.send(congratulations_message)
            except:
                return redirect(url_for('get_application', ClubId=str(ClubId)) + '?mode=viewall')
        return redirect(url_for('get_application', ClubId=str(ClubId)) + '?mode=viewall')