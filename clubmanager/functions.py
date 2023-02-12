# Import libraries
import uuid
from datetime import datetime

# custom
from clubmanager.models import ApplicationQuestions, ClubRoles, Clubs, QuestionAnswers, Students

# Create UUID generator function
def generate_UUID():
    id = str(uuid.uuid4())
    return id

def uniqueRoles(ClubId):
    roles_and_descriptions = ClubRoles.query.filter(ClubRoles.ClubId==str(ClubId)).all()
    roles = []
    rolesId = []
    role_descriptions = []
    for row in roles_and_descriptions:
        if row.Role != None and roles.count(row.Role) == 0:
            roles.append(row.Role)
            rolesId.append(row.RoleId)
        if row.RoleDescription != None and role_descriptions.count(row.RoleDescription) == 0:
            role_descriptions.append(row.RoleDescription)
    return roles, role_descriptions, rolesId

def rolespecificquestions(RoleId):
    rolespecificquestions_db = ApplicationQuestions.query.filter(ApplicationQuestions.RoleId==str(RoleId)).all()
    rolespecificquestions = []
    rolespecificquestions_ids = []
    for row in rolespecificquestions_db:
        if row.Question != None:
            rolespecificquestions.append(row.Question)
            rolespecificquestions_ids.append(row.ApplicationQuestionId)
    return rolespecificquestions, rolespecificquestions_ids

def rolespecificquestion_maxlength(RoleId):
    db_query = ApplicationQuestions.query.filter(ApplicationQuestions.RoleId==str(RoleId))
    rolespecificquestion_maxlengths = []
    for row in db_query:
        rolespecificquestion_maxlengths.append(row.LengthOfResponse)
    return rolespecificquestion_maxlengths

def generalquestions(ClubId):
    db_query = ApplicationQuestions.query.filter(ApplicationQuestions.ClubId==str(ClubId), ApplicationQuestions.RoleId==None)
    generalquestions = []
    generalquestions_ids = []
    for row in db_query:
        generalquestions.append(row.Question)
        generalquestions_ids.append(row.ApplicationQuestionId)
    return generalquestions, generalquestions_ids

def generalquestions_maxlength(ClubId):
    db_query = ApplicationQuestions.query.filter(ApplicationQuestions.ClubId==str(ClubId), ApplicationQuestions.RoleId==None)
    generalquestions_maxlengths = []
    for row in db_query:
        generalquestions_maxlengths.append(row.LengthOfResponse)
    return generalquestions_maxlengths

# Will return all the clubs logged in user owns  
def getUserOwnedClubs(user):
    clubs = Clubs.query.filter(Clubs.StudentId == user).all()
    return clubs

# Functions that validate
def validate_club_creation(FlaskForm):
    form = FlaskForm
    errors_in_clubcreation = ['', '']
    checkifclubemailisunique = Clubs.query.filter_by(ClubContactEmail=form.ClubContactEmail.data).first()
    if form.AppStartDate.data >= form.AppEndDate.data or str(form.AppStartDate.data) < str(datetime.now().date()):
        errors_in_clubcreation[0] = 'Invalid date'
    if checkifclubemailisunique != None:
        errors_in_clubcreation[1] = 'Email already exists'
    condition_1_for_date = str(form.AppStartDate.data) >= str(datetime.now().date())
    condition_2_for_date = form.AppStartDate.data < form.AppEndDate.data
    condition_3_for_email = checkifclubemailisunique == None
    return errors_in_clubcreation, condition_1_for_date, condition_2_for_date, condition_3_for_email

# def show_club_applications(ClubId):
    

