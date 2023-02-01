# Import libraries
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap

app = Flask(__name__)
app.config['SECRET_KEY'] = 'Secretshhh'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///C:\\Users\\Hetav\\Documents\\SchoolClubManager\\clubmanager.db'
Bootstrap(app)
db = SQLAlchemy(app)

# from clubmanage import routes
from clubmanager.routes import clubapplication, dashboard, index
from clubmanager.routes.club import club