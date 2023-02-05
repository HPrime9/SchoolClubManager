# Import libraries
from flask import render_template, redirect, url_for, request
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField
from wtforms.validators import InputRequired, Email, Length
from flask_login import login_required, current_user
from sqlalchemy import delete

# Import custom libraries
from clubmanager import app, db
from clubmanager.models import Club, ApplicationQuestions, ClubRole
from clubmanager.functions import generate_UUID, uniqueRoles, rolespecificquestions
from clubmanager.flaskforms import ClubRoleForm

@app.route('/clubs/<uuid:ClubId>/roles', methods=['POST'])
@app.route('/clubs/<uuid:ClubId>/roles/<uuid:RoleId>', methods=['POST'])
@login_required
def create_update_delete_roles(ClubId = '', RoleId = ''):
    mode = request.args.get('mode') 
    form = ClubRoleForm() 
    Role = request.form.getlist('Role')
    RoleDescription = request.form.getlist('RoleDescription')
    updClubRole = ClubRole.query.get_or_404(str(RoleId))
    if mode == 'new':
        if form.validate_on_submit:
            for i in range(len(Role)):
                if Role[i].strip() != '' and RoleDescription[i].strip() != '':
                    roleid = generate_UUID()
                    new_role_and_description = ClubRole(RoleId=roleid, ClubId=str(ClubId), Role=Role[i], RoleDescription=RoleDescription[i]) 
                    db.session.add(new_role_and_description)
                    try:
                        db.session.commit()
                    except:
                        return 'there was problem adding role and description'
            return redirect(url_for('get_club', ClubId=ClubId))
    elif mode == 'update':
        if form.validate_on_submit: 
                if request.form['Role'].strip() != '' and request.form['RoleDescription'].strip() != '':
                    updClubRole.Role = request.form['Role']
                    updClubRole.RoleDescription = request.form['RoleDescription']
                    try:
                        db.session.commit()
                        return redirect(url_for('get_club', ClubId=ClubId))
                    except:
                        return 'there was problem updating'
    elif mode == 'delete':
        delete_rows = delete(ApplicationQuestions).where(ApplicationQuestions.RoleId == str(RoleId))
        role_to_del = ClubRole.query.filter_by(RoleId=str(RoleId)).first()
        try:
            db.session.delete(role_to_del)
            db.session.commit()
            rows = db.session.execute(delete_rows)
            print(rows)
            return redirect(url_for('get_club', ClubId=ClubId))
        except:
            return 'sorry could not delete'
    else:
        return 'error'









    # stmt = select(ApplicationQuestions).where(ApplicationQuestions.ClubId == str(ClubId), ApplicationQuestions.Role == Role)
    # print(stmt)
    # rows = db.session.execute(stmt)
    # for row in rows:
    #     print(row)


        ################################# Check if roleid in update corresponds to actual role or find better method