from dependencies.database import Database

db = Database()

class Resume:
    def __init__(self, userid):
        self.userid = userid
        self.user_name = ''
        self.contact_email = ''
        self.contact_phone = ''
        self.contact_linkedin = ''
        self.contact_portfolio = ''
        self.address = '' # new

        self.summary = ''
        self.brand_statement = '' #new
        self.work_history = []
        self.projects = []
        self.education = []
        self.certifications = []
        self.awards = []
        self.skills = []

        self.load_from_db()
    def load_from_db(self):
        """Loads user resume from database."""
        resume = db.get_resume(self.userid)

        self.user_name = resume['name']
        self.contact_email = resume['contact']['email']
        self.contact_phone = resume['contact']['phone']
        self.contact_linkedin = resume['contact']['linkedin']
        self.contact_portfolio = resume['contact']['portfolio']

        self.summary = resume['summary']
        self.work_history = resume['work_history']
        self.projects = resume['projects']
        self.education = resume['education']
        self.certifications = resume['certifications']
        self.awards = resume['awards']
        self.skills = resume['skills']

    def to_dict(self):
        resume = {
            "name": self.user_name,
            "contact": {
                "email": self.contact_email,
                "phone": self.contact_phone,
                "linkedin": self.contact_linkedin,
                "portfolio": self.contact_portfolio,
            },
            "summary": self.summary,
            "work_history": self.work_history,
            "projects": self.projects,
            "education": self.education,
            "certifications": self.certifications,
            "skills": self.skills,
            "awards": self.awards
        }

        return resume

    def remove_leading_char(self, string: str):
        string = string.strip()

        if string[0].isalnum():
            return string
        else:
            string = string[1:].strip()
            return string

    def remove_ending_char(self, string: str):
        string = string.strip()

        if string[-1].isalnum():
            return string
        else:
            string = string[0:-1].strip()
            return string

    def update(self):
        """Updates Resume"""
        resume = self.to_dict()

        db.update_resume(self.userid, resume)

    def create_initial_resume(self):
        """Creates the initial resume with contact info obtained from account creation"""
        resume = self.to_dict()

        db.add_resume(self.userid, resume)

    def add_work_history(self,job_title, company_name, description, start_month, start_year,
                         end_month, end_year, currently_working):

        split_description = description.splitlines() # split description lines to apply our own formatting
        split_description = [self.remove_leading_char(desc) for desc in split_description] # remove leading styling
        split_description = [self.remove_ending_char(desc) for desc in
                             split_description] # remove ending to apply consistent endings

        work_history = {
            "job_title": job_title,
            "company_name": company_name,
            "date_started": {
                "month": start_month,
                "year": start_year,
            },
            "date_ended": {
                "month": end_month,
                "year": end_year,
            },
            "currently_working": currently_working,
            "description": description,
            "description_split": split_description
        }

        self.work_history.append(work_history)
        self.update()

    def update_work_history(self, index, job_title, company_name, description, start_month, start_year,
                         end_month, end_year, currently_working):
        split_description = description.splitlines() # split description lines to apply our own formatting
        split_description = [self.remove_leading_char(desc) for desc in split_description] # remove leading styling
        split_description = [self.remove_ending_char(desc) for desc in
                             split_description]  # remove ending to apply consistent endings

        work_history = {
            "job_title": job_title,
            "company_name": company_name,
            "date_started": {
                "month": start_month,
                "year": start_year,
            },
            "date_ended": {
                "month": end_month,
                "year": end_year,
            },
            "currently_working": currently_working,
            "description": description,
            "description_split": split_description
        }

        self.work_history[index] = work_history
        self.update()

    def delete_work_history(self, index):
        self.work_history.pop(index)
        self.update()

    def add_project(self, project_title, date_month, date_year, description):
        project_history = {
            "project_title": project_title,
            "date_completed": {
                "month": date_month,
                "year": date_year,
            },
            "description": description,
        }

        self.projects.append(project_history)

    def add_education(self, school_name, degree, field_of_study, start_month, start_year,
                      end_month=None, end_year=None, grade=None, activities=None, description=None):
        education = {
            "school_name": school_name,
            "degree": degree,
            "field_of_study": field_of_study,
            "date_started": {
                "month": start_month,
                "year": start_year,
            },
            "graduation_date": {
                "month": end_month,
                "year": end_year,
            },
            "grade": grade,
            "activities": activities,
            "description": description,
        }

        self.education.append(education)
        self.update()

    def update_education(self,index, school_name, degree, field_of_study, start_month, start_year,
                      end_month=None, end_year=None, grade=None, activities=None, description=None):
        education = {
            "school_name": school_name,
            "degree": degree,
            "field_of_study": field_of_study,
            "date_started": {
                "month": start_month,
                "year": start_year,
            },
            "graduation_date": {
                "month": end_month,
                "year": end_year,
            },
            "grade": grade,
            "activities": activities,
            "description": description,
        }

        self.education[index] = education
        self.update()

    def delete_education(self, index):
        self.education.pop(index)
        self.update()

    def add_certification(self, name, issuing_org, issued_month, issued_year, expire_month,
                          expire_year, cred_id=None, cred_url=None):
        certification = {
            "name": name,
            "issuing_org": issuing_org,
            "date_issued": {
                "month": issued_month,
                "year": issued_year,
            },
            "date_expired": {
                "month": expire_month,
                "year": expire_year,
            },
            "credential_id": cred_id,
            "credential_url": cred_url,
        }

        self.certifications.append(certification)

