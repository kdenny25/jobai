import os
from docx2pdf import convert
from flask import Blueprint, render_template, request, redirect
from docxtpl import DocxTemplate
from dependencies import Database, Resume
from datetime import datetime

resume_builder = Blueprint("resume_builder", __name__,
                           template_folder="templates",
                           static_folder='static',
                           static_url_path='/static/resume_builder')

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
    #print(resume)
    years = gen_years()

    return render_template('my_resume.html', resume=resume, months=Months, years=years)

@resume_builder.post('/my_resume/update_contact')
def update_contact():
    resume = Resume(0)

    resume.user_name = request.form.get('name')
    resume.contact_email = request.form.get('email')
    resume.contact_phone = request.form.get('phone')
    resume.contact_linkedin = request.form.get('linkedin')
    resume.contact_portfolio = request.form.get('portfolio')

    resume.update()

    return redirect("/my_resume")

@resume_builder.post('/my_resume/update_summary')
def update_summary():
    resume = Resume(0)

    resume.summary = request.form.get('summary')
    resume.update()

    return redirect("/my_resume")

@resume_builder.post('/my_resume/update_experience')
def update_experience():
    resume = Resume(0)

    index = int(request.form.get('ex_index'))
    job_title = request.form.get('ex_job_title')
    company_name = request.form.get('ex_company')
    current = 'ex_current' in request.form
    start_month = request.form.get('ex_start_month')
    start_year = request.form.get('ex_start_year')
    end_month = request.form.get('ex_end_month') if current is False else None
    end_year = request.form.get('ex_end_year') if current is False else None
    description = request.form.get('ex_description')


    resume.update_work_history(index=index, job_title=job_title, company_name=company_name, currently_working=current,
                               start_month=start_month, start_year=start_year, end_month=end_month, end_year=end_year,
                               summary='', description=description)

    return redirect("/my_resume")

@resume_builder.post('/my_resume/add_experience')
def add_experience():
    resume = Resume(0)

    job_title = request.form.get('add_job_title')
    company_name = request.form.get('add_company')
    current = 'add_current' in request.form
    start_month = request.form.get('add_start_month')
    start_year = request.form.get('add_start_year')
    end_month = request.form.get('add_end_month') if current is False else None
    end_year = request.form.get('add_end_year') if current is False else None
    description = request.form.get('add_description')


    resume.add_work_history(job_title=job_title, company_name=company_name, currently_working=current,
                               start_month=start_month, start_year=start_year, end_month=end_month, end_year=end_year,
                               summary='', description=description)

    return redirect("/my_resume")

@resume_builder.get('/my_resume/delete_ex')
def delete_experience():
    resume = Resume(0)
    experience_id = int(request.values.get("_exid")) - 1

    resume.delete_work_history(experience_id)

    return redirect("/my_resume")

@resume_builder.post('/my_resume/add_education')
def add_education():
    resume = Resume(0)

    school_name = request.form.get('school_name')
    degree = request.form.get('add_degree')
    field_of_study = request.form.get('add_field_of_study')
    grade = request.form.get('add_grade')
    start_month = request.form.get('add_start_month')
    start_year = request.form.get('add_start_year')
    end_month = request.form.get('add_end_month')
    end_year = request.form.get('add_end_year')
    activities = request.form.get('add_activities')
    description = request.form.get('add_description')

    resume.add_education(school_name=school_name, degree=degree, field_of_study=field_of_study, grade=grade,
                         start_month=start_month, start_year=start_year, end_month=end_month, end_year=end_year,
                         activities=activities, description=description)

    return redirect("/my_resume")

@resume_builder.post('/my_resume/edit_education')
def edit_education():
    resume = Resume(0)

    index = request.form.get('edu_index')
    school_name = request.form.get('edit_school_name')
    degree = request.form.get('edit_degree')
    field_of_study = request.form.get('edit_field_of_study')
    grade = request.form.get('edit_grade')
    start_month = request.form.get('edit_start_month')
    start_year = request.form.get('edit_start_year')
    end_month = request.form.get('edit_end_month')
    end_year = request.form.get('edit_end_year')
    activities = request.form.get('edit_activities')
    description = request.form.get('edit_description')

    resume.update_education(index=index, school_name=school_name, degree=degree, field_of_study=field_of_study,
                            grade=grade, start_month=start_month, start_year=start_year, end_month=end_month,
                            end_year=end_year, activities=activities, description=description)
    return redirect('/my_resume')

@resume_builder.get('/my_resume/delete_education')
def delete_education():
    resume = Resume(0)
    education_id = int(request.values.get("_exid")) - 1

    resume.delete_education(education_id)

    return redirect("/my_resume")

@resume_builder.get('/my_resume/templates')
def templates():
    resume = Resume(0)

    doc = DocxTemplate('resume_skeletons/ATS_Resume_Template.docx')
    context = resume.to_dict()
    doc.render(context)
    doc.save('apps/resume_builder/static/generated.docx')
    #convert('apps/resume_builder/static/generated.docx')

    return render_template('resume_templates.html')

@resume_builder.get('/my_resume/view_template')
def view_template():
    resume = Resume(0).to_dict()
    return render_template('resume_skeletons/ATS_Resume_Template.html', resume=resume)
