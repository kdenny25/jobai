from flask import Flask, request, render_template, url_for, redirect, flash, session
from flask_wtf.csrf import CSRFProtect
from flask_login import LoginManager, current_user,login_required, login_user, logout_user
import os, sys
from datetime import datetime
import math
import spacy
from dependencies import Database, Resume, Analysis
from apps.resume_builder.routes import resume_builder

db = Database()

# nlp data
nlp = spacy.load('en_core_web_md')

base_dir = '.'

app = Flask(__name__,
            static_folder=os.path.join(base_dir, 'static'),
            template_folder=os.path.join(base_dir, 'templates'),)

app.register_blueprint(resume_builder)

# csrf protection
csrf = CSRFProtect(app)
app.secret_key = b'_53oi3uriq9pifpff;apl'



@app.route('/')
def hello_world():  # put application's code here
    return render_template('index.html')

@app.route('/applications/')
def redir_applications():
    return redirect('/applications/1')

@app.route('/applications/<page>')
def applications(page):
    search = request.values.get("_search")

    if search is not None:
        # todo: must implement postgresql vector search for this
        job_applications = []
        jobs = db.get_jobs_listings(filter="active")
        search_doc = nlp(search)
        if jobs != None:
            for job in jobs:
                job_title_string = job[1]
                job_company_string = job[2]
                job_title_doc = nlp(job_title_string)
                job_company_doc = nlp(job_company_string)
                if job_title_doc.similarity(search_doc) > 0.2 or job_company_doc.similarity(search_doc) > 0.2:
                    job_applications.append(job)

    else:
        job_applications = db.get_jobs_listings(filter="active")

    job_id = request.values.get("_jobid")
    job_details = None
    todays_date = datetime.today().strftime("%Y-%m-%d")

    current_page = int(page)
    num_apps_per_page = 15
    num_pages = math.ceil(len(job_applications)/num_apps_per_page)
    start = (current_page-1) * num_apps_per_page
    end = (current_page * num_apps_per_page)

    job_applications = job_applications[start:end]

    application_metrics = {
        "active_apps": db.total_active_applications(),
        "applied_month": db.monthly_applications()
    }

    # if a job is selected then hide the add job form
    if job_id == None:
        add_job = True
    else:
        add_job = False
        job_details = db.view_job_listing(job_id)

    return render_template('applications.html', job_applications=job_applications, add_job=add_job,
                           job_details=job_details, current_page=current_page, num_pages=num_pages,
                           todays_date=todays_date, app_metrics=application_metrics)

@app.post('/app_search')
def app_search():
    search_term = request.form.get('search')
    return redirect(f'/applications/1?_search={search_term}')

@app.post('/add_job')
def add_job():
    date_applied = request.form.get('date_applied')
    job_title = request.form.get('job_title')
    company_name = request.form.get('company_name')
    company_website = request.form.get('company_website')
    salary_low = request.form.get('salary_low')
    salary_low = None if salary_low == '' else float(salary_low)
    salary_high = request.form.get('salary_high')
    salary_high = None if salary_high == '' else float(salary_high)
    job_description = request.form.get('job_description')

    db.create_job_listing(job_title, company_name, company_website, job_description,
                          salary_low, salary_high, date_applied)
    return redirect('/applications/1')

@app.get('/applications/archive')
def archive_job():
    job_id = request.values.get('_id')
    db.set_active_job_listing(job_id, 0)


    return redirect('/applications')

@app.post('/applications/analysis')
def app_analysis():
    resume = Resume(0)


    date_applied = request.form.get('date_applied')
    job_title = request.form.get('job_title')
    company_name = request.form.get('company_name')
    company_website = request.form.get('company_website')
    salary_low = request.form.get('salary_low')
    salary_low = None if salary_low == '' else float(salary_low)
    salary_high = request.form.get('salary_high')
    salary_high = None if salary_high == '' else float(salary_high)
    job_description = request.form.get('job_description')

    job_details = {
        "date_applied": date_applied,
        "job_title": job_title,
        "company_name": company_name,
        "company_website": company_website,
        "salary_low": salary_low,
        "salary_high": salary_high,
        "job_description": job_description
    }

    analyze = Analysis(resume, job_description)

    app_key_phrases = analyze.key_phrase_counts()
    #print(app_key_phrases)

    return render_template('application_analysis.html', app_key_phrases=app_key_phrases, job_details=job_details)

if __name__ == '__main__':
    app.run()
