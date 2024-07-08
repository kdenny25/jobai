import spacy
from spacy.matcher import Matcher
import re

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
    def __init__(self, resume, job_listing):
        self.resume = resume
        self.merged_resume = self.combine_resume()
        self.job_listing = job_listing

    def key_phrase_counts(self):
        listing_keyphrases = self.keyphrases(self.job_listing)

        for keyphrase, value in listing_keyphrases.items():
            resume_count = len(re.findall(keyphrase, self.merged_resume))
            listing_keyphrases[keyphrase] = (value, resume_count)

        return listing_keyphrases

    def combine_resume(self):
        # merge resume
        merged_resume = (f"{self.resume.summary} ")

        for wh in self.resume.work_history:
            merged_resume = f"{merged_resume} {wh['job_title']} {wh['description']}"

        for edu in self.resume.education:
            merged_resume = f"{merged_resume} {edu['degree']} {edu['activities']} {edu['description']}"

        return merged_resume

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