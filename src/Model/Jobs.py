import yake
from jobspy import scrape_jobs
from transformers import pipeline
import spacy

token_skill_classifier = pipeline(model="jjzha/jobbert_skill_extraction", aggregation_strategy="first")
token_knowledge_classifier = pipeline(model="jjzha/jobbert_knowledge_extraction", aggregation_strategy="first")

import re

def clean_keyword(keyword):
    keyword = keyword.lower()
    
    keyword = re.sub(r'https?://\S+|www\.\S+', '', keyword)
    keyword = re.sub(r'\S+@\S+', '', keyword)
    keyword = re.sub(r'[^\w\s-]', '', keyword)
    keyword = keyword.replace('-', ' ') 
    keyword = ' '.join(keyword.split())
    
    stopwords = {'a', 'an', 'the', 'and', 'or', 'of', 'for', 'in', 'to', 'with'}
    keyword = ' '.join([word for word in keyword.split() if word not in stopwords])
    
    return keyword.strip()

def aggregate_span(results):
    new_results = []
    current_result = results[0]

    for result in results[1:]:
        if result["start"] == current_result["end"] + 1:
            current_result["word"] += " " + result["word"]
            current_result["end"] = result["end"]
        else:
            new_results.append(current_result)
            current_result = result

    new_results.append(current_result)

    return new_results

def hugging_face(text, max_length=512):
    # Split text into chunks of max_length tokens
    chunks = [text[i:i + max_length] for i in range(0, len(text), max_length)]
    
    output_skills = []
    output_knowledge = []

    for chunk in chunks:
        chunk_skills = token_skill_classifier(chunk)
        chunk_knowledge = token_knowledge_classifier(chunk)

        # Process skills with cleaning
        for result in chunk_skills:
            if result.get("entity_group"):
                result["entity"] = "Skill"
                del result["entity_group"]
        output_skills.extend(chunk_skills)

        # Process knowledge
        for result in chunk_knowledge:
            if result.get("entity_group"):
                result["entity"] = "Knowledge"
                del result["entity_group"]
        output_knowledge.extend(chunk_knowledge)

    # Aggregate spans if necessary
    if len(output_skills) > 0:
        output_skills = aggregate_span(output_skills)
    if len(output_knowledge) > 0:
        output_knowledge = aggregate_span(output_knowledge)

    return {"text": text, "entities": output_skills}, {"text": text, "entities": output_knowledge}

def extract_with_spacy(text):
    nlp = spacy.load("en_core_web_sm")
    
    doc = nlp(text)
    entities = []
    
    for ent in doc.ents:
        if ent.label_ in ["ORG", "PRODUCT", "TECH", "SKILL"]: 
            entities.append({
                "word": clean_keyword(ent.text),
                "entity": "Skill" if ent.label_ in ["TECH", "SKILL"] else "Knowledge",
                "start": ent.start_char,
                "end": ent.end_char
            })
    
    return {"text": text, "entities": entities}

class Job:
    def __init__(self, job_title, job_description, job_location, job_employer, posted_at, job_url):
        self.job_title = job_title
        self.job_description = job_description
        self.job_location = job_location
        self.job_employer = job_employer
        self.posted_at = posted_at
        self.job_url = job_url
        self.keywords = []


    def get_keywords(self, model="HUGGINGFACE"):
        if (model == "YAKE"):
            kw_extractor = yake.KeywordExtractor()
            self.keywords = kw_extractor.extract_keywords(self.job_description)
            self.keywords = [word[0].lower() for word in self.keywords]
        elif (model == "HUGGINGFACE"):
            self.keywords = [clean_keyword(i["word"]) for i in hugging_face(self.job_description)[1]["entities"]]
        elif (model == "SPACY"):
            self.keywords = [clean_keyword(i["word"]) for i in extract_with_spacy(self.job_description)["entities"]]

        return list(set(self.keywords))

def get_jobs(job_title, job_location, number_of_results=20, hours_old=72):
    jobs = scrape_jobs(
        site_name=["indeed"],
        search_term=job_title,
        location=job_location,
        results_wanted=number_of_results,
        hours_old=hours_old,
    )
    
    job_instances = []
    for i in range(len(jobs)):
        job_instance = Job(
            job_title=jobs.iloc[i]["title"],
            job_description=jobs.iloc[i]['description'],
            job_location=jobs.iloc[i]["location"],
            job_employer=jobs.iloc[i]["company"],
            posted_at=jobs.iloc[i]["date_posted"],
            job_url=jobs.iloc[i]["job_url"]
        )

        job_instances.append(job_instance)

    return job_instances
