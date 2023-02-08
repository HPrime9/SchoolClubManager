# Import libraries
from flask import render_template

# import custom models
from clubmanager import app

@app.route('/')
def index():
    return render_template('index.html')
    