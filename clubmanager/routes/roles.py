# Import libraries
from flask import redirect, url_for, request, flash
from flask_login import login_required
from sqlalchemy import delete

# Import custom libraries
from clubmanager import app, db
from clubmanager.models import ApplicationQuestions, ClubRoles
from clubmanager.functions import generate_UUID
from clubmanager.flaskforms import ClubRoleForm

# Create app routes
@app.route('/clubs/<uuid:ClubId>/roles', methods=['POST'])
@app.route('/clubs/<uuid:ClubId>/roles/<uuid:RoleId>', methods=['POST'])
@login_required
def create_update_delete_roles(ClubId, RoleId = ''):
    # get the mode in the url
    mode = request.args.get('mode')

    # get roles and role descriptions the user entered 
    Role = request.form.getlist('Role')
    RoleDescription = request.form.getlist('RoleDescription')

    # add a role and its description in the table ClubRole if the user is creating a role
    if mode == 'new':
        for i in range(len(Role)):
            if Role[i].strip() != '' and RoleDescription[i].strip() != '':
                roleid = generate_UUID()
                new_role_and_description = ClubRoles(RoleId=roleid, ClubId=str(ClubId), Role=Role[i], RoleDescription=RoleDescription[i]) 
                db.session.add(new_role_and_description)
                try:
                    db.session.commit()
                except:
                    return redirect(url_for('get_club', ClubId=str(ClubId)) + '?mode=update#nav-generalquestions')
    
    # update the role and/or its description
    elif mode == 'update':
        if request.form['Role'].strip() != '' and request.form['RoleDescription'].strip() != '':
            updClubRole = ClubRoles.query.filter_by(RoleId=str(RoleId)).first()
            updClubRole.Role = request.form['Role']
            updClubRole.RoleDescription = request.form['RoleDescription']
            try:
                db.session.commit()
            except:
                return redirect(url_for('get_club', ClubId=str(ClubId)) + '?mode=update#nav-generalquestions')
    
    # delete the role and its description
    elif mode == 'delete':
        delete_rows = delete(ApplicationQuestions).where(ApplicationQuestions.RoleId == str(RoleId))
        role_to_del = ClubRoles.query.filter_by(RoleId=str(RoleId)).first()
        try:
            db.session.delete(role_to_del)
            db.session.execute(delete_rows)
            db.session.commit()
        except:
            return redirect(url_for('get_club', ClubId=str(ClubId)) + '?mode=update#nav-generalquestions')
    
    # load the same page again
    return redirect(url_for('get_club', ClubId=str(ClubId)) + '?mode=update#nav-roles')