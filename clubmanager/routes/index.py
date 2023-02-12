# Import libraries
from flask import render_template

# import custom libraries
from clubmanager import app

# Create index route
@app.route('/')
def index():
    # render landing page of website
    return render_template('index.html')
    