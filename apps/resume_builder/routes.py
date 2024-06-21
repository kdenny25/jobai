from flask import Blueprint, render_template, request, redirect
from dependencies import Database, Resume
from datetime import datetime

resume_builder = Blueprint("resume_builder", __name__,
                           template_folder="templates")

Months = [
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December"
]

def gen_years():
    current_year = datetime.today().year
    last_year = current_year-100

    years = [str(Y) for Y in range(current_year, last_year-1, -1)]

    return years

@resume_builder.route('/my_resume')
def my_resume():
    # temporarily use 1 to indicate it's my userid
    resume = Resume(0).to_dict()
    years = gen_years()

    return render_template('my_resume.html', resume=resume, months=Months, years=years)

@resume_builder.post('/update_contact')
def update_contact():
    resume = Resume(0)

    resume.user_name = request.form.get('name')
    resume.contact_email = request.form.get('email')
    resume.contact_phone = request.form.get('phone')
    resume.contact_linkedin = request.form.get('linkedin')
    resume.contact_portfolio = request.form.get('portfolio')

    resume.update()

    return redirect("/my_resume")

@resume_builder.post('/update_summary')
def update_summary():
    resume = Resume(0)

    resume.summary = request.form.get('summary')
    resume.update()

    return redirect("/my_resume")
