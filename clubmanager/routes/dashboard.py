# Import libraries
from flask import render_template, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user

# Import custom libraries
from clubmanager import app, db
from clubmanager.models import Student
from clubmanager.functions import generate_UUID, getUserOwnedClubs
from clubmanager.flaskforms import LoginForm, RegisterForm

# Initialize variables
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'get_login'

@login_manager.user_loader
def load_user(user_id):
    return Student.query.get(user_id)

# Create routes
@app.route('/login/dashboard', methods=['GET'])
def get_login():
    form = LoginForm()
    return render_template('login.html', form=form)

@app.route('/login/dashboard', methods=['POST'])
def create_login():
    form = LoginForm()
    if form.validate_on_submit():
        user = Student.query.filter_by(StudentNum=form.StudentNum.data).first()
        if user:
            if check_password_hash(user.Password, form.Password.data):
                login_user(user, remember=True)
                return redirect(url_for('dashboard'))
        flash('Incorrect Username or Password!', 'error') #warning, info, error
        return render_template('login.html', form=form)

@app.route('/register/dashboard', methods=['GET'])
def get_registration():
    form = RegisterForm()
    errors = ['', '', '']
    return render_template('register.html', form=form, errors=errors)

@app.route('/register/dashboard', methods=['POST'])
def create_user():
    form = RegisterForm()
    checkifusernameisunique = Student.query.filter_by(Username=form.Username.data).first()
    checkifstudentnumisunique = Student.query.filter_by(StudentNum=form.StudentNum.data).first()
    checkifemailisunique = Student.query.filter_by(Email=form.Email.data).first()
    errors = ['', '', '']
    if checkifusernameisunique != None:
        errors[0] = ('Username is already taken')
    if checkifstudentnumisunique != None:
        errors[1] = ('Student Number is already taken')
    if checkifemailisunique != None:
        errors[2] = ('Email already exists')
    condition = checkifusernameisunique == None and checkifstudentnumisunique == None and checkifemailisunique == None
    if form.validate_on_submit():
        if condition:
            hashed_Password = generate_password_hash(form.Password.data, method='sha256')
            new_user = Student(id=generate_UUID(), FirstName=form.FirstName.data, LastName=form.LastName.data, Username=form.Username.data, StudentNum=form.StudentNum.data, Email=form.Email.data, Password=hashed_Password, Grade=form.Grade.data, School=form.School.data)
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            return redirect(url_for('dashboard'))

    return render_template('register.html', form=form, errors=errors)

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