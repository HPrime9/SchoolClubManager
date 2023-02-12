# Import libraries
from flask import render_template, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user

# Import custom libraries
from clubmanager import app, db
from clubmanager.models import Students
from clubmanager.functions import generate_UUID, getUserOwnedClubs
from clubmanager.flaskforms import LoginForm, RegisterForm

# Initialize variables
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'get_login'

@login_manager.user_loader
def load_user(user_id):
    return Students.query.get(user_id)

# Create routes
@app.route('/login/dashboard', methods=['GET'])
def get_login():
    # initialize form
    form = LoginForm()

    # render login page
    return render_template('login.html', form=form)

@app.route('/login/dashboard', methods=['POST'])
def create_login():
    # initialize form
    form = LoginForm()

    # check if the user exists in the database
    if form.validate_on_submit():
        user = Students.query.filter_by(StudentNum=form.StudentNum.data).first()
        if user:
            if check_password_hash(user.Password, form.Password.data):
                login_user(user, remember=True)
                return redirect(url_for('dashboard'))
        flash('Incorrect Username or Password!', 'error') #warning, info, error

        # render login page
        return render_template('login.html', form=form)

@app.route('/register/dashboard', methods=['GET'])
def get_registration():
    # initialize form
    form = RegisterForm()

    # initialize blank errors list
    errors = ['', '', '']

    # render registration page
    return render_template('register.html', form=form, errors=errors)

@app.route('/register/dashboard', methods=['POST'])
def create_user():
    # initialize form and other variables associated with checking the validity of the registration information
    form = RegisterForm()
    checkifusernameisunique = Students.query.filter_by(Username=form.Username.data).first()
    checkifstudentnumisunique = Students.query.filter_by(StudentNum=form.StudentNum.data).first()
    checkifemailisunique = Students.query.filter_by(Email=form.Email.data).first()
    errors = ['', '', '']

    # check the validity of the registration information entered and display errors accordingly
    if checkifusernameisunique != None:
        errors[0] = ('Username is already taken')
    if checkifstudentnumisunique != None:
        errors[1] = ('Student Number is already taken')
    if checkifemailisunique != None:
        errors[2] = ('Email already exists')
    condition = checkifusernameisunique == None and checkifstudentnumisunique == None and checkifemailisunique == None

    # create a new user if registration information is valid and hide password for security reasons
    if form.validate_on_submit():
        if condition:
            hashed_Password = generate_password_hash(form.Password.data, method='sha256')
            new_user = Students(id=generate_UUID(), FirstName=form.FirstName.data, LastName=form.LastName.data, Username=form.Username.data, StudentNum=form.StudentNum.data, Email=form.Email.data, Password=hashed_Password, Grade=form.Grade.data, School=form.School.data)
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            return redirect(url_for('dashboard'))
    
    # render registration page
    return render_template('register.html', form=form, errors=errors)

@app.route('/dashboard')
@login_required
def dashboard():
    # get all the clubs the user owns to display on their dashboard
    userClubCatalogue = getUserOwnedClubs(current_user.id)

    # initialize variable
    truthy = True

    # set truthy as False if the user owns clubs
    if userClubCatalogue:
        truthy = False
    
    # render dashboard page
    return render_template('dashboard.html', truthy=truthy, name=current_user.FirstName, userClubCatalogue=userClubCatalogue) 

@app.route('/logout')
@login_required
def logout():
    # logout the current user if they click logout
    logout_user()

    # redirect to the landing page
    return redirect(url_for('index'))