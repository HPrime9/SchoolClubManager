# Import libraries
import uuid
from datetime import datetime

# custom
from clubmanager.models import ApplicationQuestions, ClubRole, Club, QuestionAnswer

# Create UUID generator function
def generate_UUID():
    id = str(uuid.uuid4())
    return id

def uniqueRoles(ClubId):
    roles_and_descriptions = ClubRole.query.filter(ClubRole.ClubId==str(ClubId)).all()
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
            rolespecificquestions_ids.append(row.QuestionId)
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
        generalquestions_ids.append(row.QuestionId)
    return generalquestions, generalquestions_ids

def generalquestions_maxlength(ClubId):
    db_query = ApplicationQuestions.query.filter(ApplicationQuestions.ClubId==str(ClubId), ApplicationQuestions.RoleId==None)
    generalquestions_maxlengths = []
    for row in db_query:
        generalquestions_maxlengths.append(row.LengthOfResponse)
    return generalquestions_maxlengths

# Will return all the clubs logged in user owns  
def getUserOwnedClubs(user):
    clubs = Club.query.filter(Club.StudentNum == user).all()
    return clubs

# Functions that validate
def validate_club_creation(FlaskForm):
    form = FlaskForm
    errors_in_clubcreation = ['', '']
    checkifclubemailisunique = Club.query.filter_by(ClubContactEmail=form.ClubContactEmail.data).first()
    if form.AppStartDate.data >= form.AppEndDate.data or str(form.AppStartDate.data) < str(datetime.now().date()):
        errors_in_clubcreation[0] = 'Invalid date'
    if checkifclubemailisunique != None:
        errors_in_clubcreation[1] = 'Email already exists'
    condition_1_for_date = str(form.AppStartDate.data) >= str(datetime.now().date())
    condition_2_for_date = form.AppStartDate.data < form.AppEndDate.data
    condition_3_for_email = checkifclubemailisunique == None
    return errors_in_clubcreation, condition_1_for_date, condition_2_for_date, condition_3_for_email

def show_club_applications(ClubId):
    db_query_questionans = QuestionAnswer.query.filter(QuestionAnswer.ClubId==str(ClubId), QuestionAnswer.Status=='submitted', QuestionAnswer.RoleId!=None)
    all_studentnums = []
    all_studentnums_to_display = []
    all_grades_to_display = []
    all_roleids_to_display = []
    all_roles_to_display = []
    total_length_of_rows = 0

    for row in db_query_questionans:
        if all_studentnums.count(row.StudentNum) == 0:
            all_studentnums.append(row.StudentNum)
            all_studentnums_to_display.append(row.StudentNum)
     
    for i in range(len(all_studentnums_to_display)):
        db_deeper_query_questionans = QuestionAnswer.query.filter(QuestionAnswer.StudentNum==all_studentnums_to_display[i], QuestionAnswer.ClubId==str(ClubId), QuestionAnswer.Status=='submitted', QuestionAnswer.RoleId!=None).first()
        all_grades_to_display.append(db_deeper_query_questionans.Grade)
        all_roleids_to_display.append(db_deeper_query_questionans.RoleId)

    for i in range(len(all_roleids_to_display)):
        role = ClubRole.query.filter_by(RoleId=str(all_roleids_to_display[i])).first().Role
        all_roles_to_display.append(role)

    total_length_of_rows = len(all_roles_to_display)

    
    return all_studentnums_to_display, all_grades_to_display, all_roleids_to_display, all_roles_to_display, total_length_of_rows

