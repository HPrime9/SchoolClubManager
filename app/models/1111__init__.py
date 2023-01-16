from flask_sqlalchemy import SQLAlchemy
from flask import current_app as app

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///C:\\Users\\Hetav\\Documents\\Club Manager\\clubmanager.db'
db1 = SQLAlchemy(app)