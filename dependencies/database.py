import psycopg2
import os
from datetime import datetime
from dotenv import dotenv_values
import json

config = dotenv_values(".env")

conn_string = (f"host={config['HOST']} "
               f"user={config['USERNAME']} "
               f"dbname={config['DBNAME']} "
               f"password={config['PASSWORD']} "
               f"sslmode={config['SSLMODE']}")
RUN_LOCATION = os.environ.get("RUNNING_IN_DOCKER", False)

class Database:
    def __init__(self):
        self.con = psycopg2.connect(conn_string)
        self.cursor = self.con.cursor()
        self.create_jobs_table()
        self.creat_resume_table()


    def create_jobs_table(self):
        self.cursor.execute("CREATE TABLE IF NOT EXISTS jobs("
                            "id SERIAL PRIMARY KEY, "
                            "jobTitle varchar(50) NOT NULL, "
                            "company varchar(50) NOT NULL,"
                            "website varchar(100) NOT NULL,"
                            "posting text NOT NULL,"
                            "salaryLow decimal,"
                            "salaryHigh decimal,"
                            "dateApplied DATE, "
                            "activeJob integer);")

        self.con.commit()

    def creat_resume_table(self):
        self.cursor.execute("CREATE TABLE IF NOT EXISTS resumes("
                            "id SERIAL PRIMARY KEY, "
                            "userid INT UNIQUE, "
                            "date_created DATE NOT NULL, "
                            "resume_info JSONB NOT NULL);")

        self.con.commit()


    ########################################################
    ################# RESUME TABLE #########################
    ########################################################
    def add_resume(self, userid, resume_info):
        """Adds only one resume per user"""

        resume_info = json.dumps(resume_info)
        date_created = datetime.today().strftime("%m-%d-%Y")
        self.cursor.execute("INSERT INTO resumes(userid, date_created, resume_info) "
                            "VALUES(%s, %s, %s) on conflict (userid) do nothing;", (userid, date_created, resume_info))
        self.con.commit()

    def get_resume(self, userid):
        self.cursor.execute("SELECT resume_info "
                            "FROM resumes "
                            "WHERE userid = %s;", (userid, ))

        resume = self.cursor.fetchall()[0][0]
        return resume

    def update_resume(self, userid, resume_info):
        """Updates resume information"""
        resume_info = json.dumps(resume_info)

        self.cursor.execute("UPDATE resumes "
                            "SET resume_info=%s "
                            "WHERE userid = %s;", (resume_info, userid))
        self.con.commit()

    ########################################################
    ################### JOBS Table #########################
    ########################################################
    def create_job_listing(self, jobTitle, company, website, posting, salaryLow, salaryHigh, dateApplied):
        salaryLow = None if salaryLow == '' else salaryLow
        salaryHigh = None if salaryHigh == '' else salaryHigh
        self.cursor.execute("INSERT INTO jobs(jobTitle, company, website, posting, salaryLow, salaryHigh, dateApplied, activeJob) "
                            "VALUES(%s, %s, %s, %s, %s, %s, %s, %s);", (jobTitle, company, website, posting, salaryLow, salaryHigh, dateApplied, 1))

        self.con.commit()

    def add_old_job_listing(self, jobTitle, company, website, posting, salaryLow, salaryHigh, dateApplied, activeJob):
        salaryLow = None if salaryLow == '' else salaryLow
        salaryHigh = None if salaryHigh == '' else salaryHigh
        self.cursor.execute("INSERT INTO jobs(jobTitle, company, website, posting, salaryLow, salaryHigh, dateApplied, activeJob) "
                            "VALUES(%s, %s, %s, %s, %s, %s, %s, %s);", (jobTitle, company, website, posting, salaryLow, salaryHigh, dateApplied, activeJob))

        self.con.commit()

    def get_jobs_listings(self, filter='all'):

        if filter == 'all':
            self.cursor.execute("SELECT id, jobTitle, company, salaryLow, salaryHigh, dateApplied, activeJob "
                                "FROM jobs;")
            jobs = self.cursor.fetchall()

        elif filter == 'active':
            self.cursor.execute("SELECT id, jobTitle, company, salaryLow, salaryHigh, dateApplied, activeJob "
                                       "FROM jobs "
                                       "WHERE activeJob = %s;", (1,))
            jobs = self.cursor.fetchall()

        elif filter == 'inactive':
            self.cursor.execute("SELECT id, jobTitle, company, salaryLow, salaryHigh, dateApplied, activeJob "
                                       "FROM jobs "
                                       "WHERE activeJob = %s;", (0,))
            jobs = self.cursor.fetchall()

        else:
            raise(f'Incorrect filter selection: {filter}. Options should be all, active or inactive')

        return jobs

    def delete_job_listing(self, id):
        self.cursor.execute("DELETE FROM jobs WHERE id=%s",(id,))
        self.con.commit()

    def set_active_job_listing(self, id, isActive):
        self.cursor.execute("UPDATE jobs "
                            "SET activeJob=%s "
                            "WHERE id=%s", (isActive, id))
        self.con.commit()

    def view_job_listing(self, id):
        self.cursor.execute("SELECT jobTitle, company, website, posting, salaryLow, salaryHigh, dateApplied "
                                  "FROM jobs WHERE id=%s;",(id,))
        job = self.cursor.fetchall()

        return job

    def monthly_applications(self):
        month = datetime.today().strftime('%m')

        self.cursor.execute("SELECT id, EXTRACT(MONTH FROM dateApplied) AS monthApplied "
                                  "FROM jobs "
                                  "WHERE EXTRACT(MONTH FROM dateApplied) = %s;", (month, ))
        job = self.cursor.fetchall()
        return job

#"WHERE strftime('%m', dateApplied) = ?", (month,)
    def edit_job_listing(self, dict):
        self.cursor.execute("UPDATE jobs "
                            "SET jobTitle=%s, company=%s, website=%s, posting=%s, salaryLow=%s, salaryHigh=%s, dateApplied=%s "
                            "WHERE id=%s",
                            (dict['jobTitle'], dict['company'], dict['website'], dict['posting'],
                             dict['salaryLow'], dict['salaryHigh'], dict['dateApplied'], dict['id']))
        self.con.commit()




    def get_tables(self):
        self.cursor.execute("select relname from pg_class where relkind='r' and relname !~ '^(pg_|sql_)';")
        tables = self.cursor.fetchall()
        print(tables)
    def drop_tables(self):
        self.cursor.execute("DROP TABLE jobs")
        self.con.commit()

        self.cursor.execute("select relname from pg_class where relkind='r' and relname !~ '^(pg_|sql_)';")
        tables = self.cursor.fetchall()
        print("Jobs Table Dropped")
        print(tables)