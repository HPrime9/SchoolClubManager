from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, PasswordField
from wtforms.validators import InputRequired, Email, Length, NumberRange
from wtforms.fields import SelectField, DateField

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

# Create a class containing basic information required to start a club
class ClubCreationForm(FlaskForm):
    ClubName = StringField('Club Name', validators=[InputRequired(), Length(min=2, max=50)])
    ClubDescription = StringField('Club Description', validators=[InputRequired(), Length(max=300)])
    AppStartDate = DateField('Application Start Date', validators=[InputRequired()], format='%Y-%m-%d')
    AppEndDate = DateField('Application End Date', validators=[InputRequired()], format='%Y-%m-%d')
    ClubContactEmail = StringField('Club Contact Email', validators=[InputRequired(), Email(), Length(max=75)])

# Create class
class ClubGeneralQuestionForm(FlaskForm):
    GeneralQuestions = StringField('General Questions', validators=[Length(max=1000)])
    GeneralQuestionsLengthOfResponse = IntegerField('Length Of Response')
    GeneralQuestionOrderNumbers = IntegerField('Question Order')

class ClubRoleForm(FlaskForm):
    Role = StringField('Roles', validators=[Length(max=500)])
    RoleDescription = StringField('Role Descriptions', validators=[Length(max=1000)])

class RoleSpecificQuestionForm(FlaskForm):
    RoleSpecificQuestion = StringField('Role Specific Questions', validators=[Length(max=1000)])
    LengthOfResponse = IntegerField('Length Of Response')
    RoleSpecificQuestionOrderNumber = IntegerField('Question Order')

class ClubApplicationForm(FlaskForm):
    SubmitApplication = StringField('General Question Answer', validators=[Length(max=1000)])
    GeneralQuestionAnswers = StringField('General Question Answer', validators=[InputRequired(), Length(max=1000)])
    SelectRole = StringField('Select Role', validators=[InputRequired(), Length(max=500)])
    RoleSpecificQuestionAnswers = StringField('Role Specific Question Answer', validators=[InputRequired(), Length(max=1000)])

# Create announcement form
class AnnouncementForm(FlaskForm):
    Header = StringField('Title', validators=[InputRequired(), Length(max=100)])
    Message = StringField('Write a Message', validators=[InputRequired(), Length(max=2000)])