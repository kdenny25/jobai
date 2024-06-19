from flask import Flask, request, render_template, url_for, redirect, flash, session
from flask_wtf.csrf import CSRFProtect
from flask_login import LoginManager, current_user,login_required, login_user, logout_user
import os, sys

from dependencies import Database

db = Database()

base_dir = '.'

app = Flask(__name__,
            static_folder=os.path.join(base_dir, 'static'),
            template_folder=os.path.join(base_dir, 'templates'),)

@app.route('/')
def hello_world():  # put application's code here
    return render_template('index.html')

@app.route('/applications')
def applications():
    job_applications = db.get_jobs_listings(filter="active")
    return render_template('applications.html', job_applications=job_applications)

if __name__ == '__main__':
    app.run()
