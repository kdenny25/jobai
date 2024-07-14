import spacy
from spacy.matcher import Matcher
from openai import OpenAI
from dotenv import dotenv_values
import json
import re

config = dotenv_values(".env")

# nlp data
nlp = spacy.load('en_core_web_md')

# nlp patterns to look for
patterns = [
    [{"POS": "ADJ"}, {"POS": "NOUN"}, {"POS": "ADP", "OP": "!"}],
    [{"POS": "NOUN"}, {"POS": "ADP"}, {"POS": "NOUN"}, {"POS": "NOUN", "OP": "!"}],
    [{"POS": "NOUN"}, {"POS": "NOUN"}],
    [{"POS": "PROPN"}, {"POS": "PROPN"}],
    [{"POS": "PROPN", "DEP": "pobj"}],
    [{"POS": "PROPN", "DEP": "conj"}],
    [{"POS": "NOUN", "DEP": "pobj"}],
    ]

class Analysis:
    def __init__(self, resume, job_description):
        self.resume = resume
        self.merged_resume = self.combine_resume()
        self.job_description = job_description
        self.client = OpenAI(
            api_key=config['AI_KEY']
        )
        self.tokens_used = 0
        self.hard_skills = {}
        self.soft_skills = {}

        self.parse_job_description()
        self.phrase_counts(self.hard_skills)
        self.phrase_counts(self.soft_skills)
        self.highlights = self.gen_highlights()

    def phrase_counts(self, skill_set):
        """Counts the number of skills that popup in the resume"""

        for keyphrase, value in skill_set.items():
            resume_count = len(re.findall(keyphrase, self.merged_resume))
            # if the resume count is less than the count
            skill_set[keyphrase] = (value, resume_count)

    def calc_scores(self):
        # hard skills score
        hard_skills_total = 0
        hard_skills_actual = 0
        for item, value in self.hard_skills.items():
            h_total = value[0]/2 + 1
            if value[1] > value[0]:
                h_actual = h_total
            else:
                h_base = 0 if value[1] == 0 else 1
                h_actual = value[1]/2 + h_base

            hard_skills_total += h_total
            hard_skills_actual += h_actual

        soft_skills_total = 0
        soft_skills_actual = 0
        for item, value in self.soft_skills.items():

            s_total = value[0]/2 + 1
            if value[1] > value[0]:
                s_actual = s_total
            else:
                s_base = 0 if value[1] == 0 else 1
                s_actual = value[1]/2 + s_base

            soft_skills_total += s_total
            soft_skills_actual += s_actual

        scores = {
            "searchability": 0,
            "hard_skills": int((hard_skills_actual/hard_skills_total)*100),
            "soft_skills": int((soft_skills_actual/soft_skills_total)*100)
        }

        return scores

    def combine_resume(self):
        # merge resume
        merged_resume = (f"{self.resume.summary} ")

        for wh in self.resume.work_history:
            merged_resume = f"{merged_resume} {wh['job_title']} {wh['summary']} {wh['highlights']}"

        for edu in self.resume.education:
            merged_resume = f"{merged_resume} {edu['degree']} {edu['activities']} {edu['description']}"

        return merged_resume

    def check_json(self, json_string:str):

        try:
            to_dict = json.loads(json_string)

        except:
            start = json_string.find("{")
            end = 0
            for idx in range(len(json_string)+1):
                if json_string[-idx] == "}":
                    end = -(idx - 1)
                    break

            to_dict = json.loads(json_string[start:end])

        return to_dict


    def parse_job_description(self):
        """Pulls a list of hard and soft skills from a job description"""
        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You will create a list of soft skills as soft_skills and "
                                              "hard skills as hard_skills each key phrase should not exceed 4 "
                                              "words and no hyphens"
                                              "and with counts of occurrences from "
                                              "the supplied user text then output the lists in JSON format "
                                              },
                {"role": "user", "content": f"{self.job_description}"}
            ]
        )
        content = response.choices[0].message.content
        print(content)

        resp_dict = self.check_json(content)
        self.tokens_used += response.usage.total_tokens
        self.hard_skills = resp_dict['hard_skills']
        self.soft_skills = resp_dict['soft_skills']

    def gen_highlights(self):
        """Generates two highlights relating to the job listing skill and users resume"""
        skill_list = list(self.soft_skills.keys()) + list(self.hard_skills.keys())
        job_list = [job['job_title'] for job in self.resume.work_history]

        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You will be provided a list of job titles and a list of skills. For each item in the "
                                              "list of skills create two examples of good job highlights using "
                                              "the skill in the examples. "
                                              "Relate the job highlight to the most relevant job titles and include "
                                              "the skill in the highlight. Return the responses in JSON "
                                              "format where the skill item is the key and a list of two examples are "
                                              "the values"},
                {"role": "user", "content": f"Resume: {job_list} \n"
                                            f"Skills: {skill_list}"}
            ]
        )
        content = response.choices[0].message.content

        print(content)
        resp_dict = self.check_json(content)
        return resp_dict

    def keyphrases(self, input):
        nlp = spacy.load('en_core_web_lg')

        matcher = Matcher(nlp.vocab)
        matcher.add("qualification", patterns)

        application_doc = nlp(input)
        matches = matcher(application_doc)

        key_phrases = {}

        prev_range = []

        for match_id, start, end in matches:
            if start not in prev_range:
                span = application_doc[start:end]
                match_text = str(span).lower()

                key_phrases[match_text] = key_phrases.get(match_text, 0) + 1
                prev_range = range(start, end)

            # span = application_doc[start:end]
            # match_text = str(span).lower()
            #
            # key_phrases[match_text] = key_phrases.get(match_text, 0) + 1
            # prev_range = range(start, end)

        to_remove = []
        # todo: merge similar key phrases
        # remove key_phrases with only 1 occurrence
        # for key_phrase, value in key_phrases.items():
        #     if value == 1:
        #         to_remove.append(key_phrase)

        for key in to_remove:
            key_phrases.pop(key)

        return key_phrases