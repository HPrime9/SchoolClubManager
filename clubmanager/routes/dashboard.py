# Import libraries
from flask import render_template, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, PasswordField
from wtforms.validators import InputRequired, Email, Length, NumberRange
from wtforms.fields import SelectField
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user

# import custom models
from clubmanager import app, db
from clubmanager.models import Student
from clubmanager.functions import generate_UUID, getUserOwnedClubs

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    return Student.query.get(user_id)

# Create login form
class LoginForm(FlaskForm):
    StudentNum = StringField('Student Number', validators=[InputRequired()])
    Password = PasswordField('Password', validators=[InputRequired(), Length(min=1, max=80)]) # cahnge password to min  8

# Create registration form
class RegisterForm(FlaskForm):
    FirstName = StringField('First Name', validators=[InputRequired(), Length(max=75)])
    LastName = StringField('Last Name', validators=[InputRequired(), Length(max=100)])
    Username = StringField('Username', validators=[InputRequired(), Length(min=3, max=36)])
    StudentNum = IntegerField('Student Number', validators=[InputRequired(), NumberRange(min=0)])
    Email = StringField('Email', validators=[InputRequired(), Email(), Length(max=75)])
    Password = PasswordField('Password', validators=[InputRequired(), Length(min=1, max=80)]) # remeber to change min to 8
    Grade = SelectField('Select Grade', choices=['3', '4', '5', '6', '7', '8', '9', '10', '11', '12'])
    School = SelectField('Select School', choices=['Turner Fenton Secondary School', 'Roberta Bondar Public School', 'T. L. Kennedy Secondary School'])

@app.route('/login/dashboard', methods=['POST', 'GET'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = Student.query.filter_by(StudentNum=form.StudentNum.data).first()
        if user:
            if check_password_hash(user.Password, form.Password.data):
                login_user(user)
                return redirect(url_for('dashboard'))
        return 'Invalid Username or Password'

    return render_template('login.html', form=form)

@app.route('/register/dashboard', methods=['POST', 'GET'])
def register():
    form = RegisterForm()
    
    if form.validate_on_submit():
        hashed_Password = generate_password_hash(form.Password.data, method='sha256')
        new_user = Student(id=generate_UUID(), FirstName=form.FirstName.data, LastName=form.LastName.data, Username=form.Username.data, StudentNum=form.StudentNum.data, Email=form.Email.data, Password=hashed_Password, Grade=form.Grade.data, School=form.School.data)
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('dashboard'))
    return render_template('register.html', form=form)

@app.route('/dashboard')
@login_required
def dashboard():
    userClubCatalogue = getUserOwnedClubs(current_user.StudentNum)
    truthy = True
    if userClubCatalogue:
        truthy = False
    return render_template('dashboard.html', truthy=truthy, name=current_user.FirstName, userClubCatalogue=userClubCatalogue) 

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))