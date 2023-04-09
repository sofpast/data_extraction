from bs4 import BeautifulSoup
import requests
import os 
import os.path
import csv 
import time 

import pandas as pd

from azure.core.credentials import AzureKeyCredential
from azure.ai.textanalytics import TextAnalyticsClient

from dotenv import load_dotenv
import nltk

import spacy

# from spacy import displaycy

nlp = spacy.load('en_core_web_sm')

# import pdb
# pdb.set_trace()

from spacy.matcher import Matcher 
from spacy.tokens import Span 
import tqdm

load_dotenv()


url = "https://www.microsoft.com/en-us/security/blog/2023/03/17/killnet-and-affiliate-hacktivist-groups-targeting-healthcare-with-ddos-attacks/"

# import module

# link for extract html data
def getdata(url):
	r = requests.get(url)
	return r.text

htmldata = getdata(url)
soup = BeautifulSoup(htmldata, 'html.parser')
data = ''
p_list = []
h2_list = []
h3_list = []
text = []
for para in soup.find_all("p"):
	print(para.get_text())
	p_list.append(para.get_text())

for h2 in soup.find_all("h2"):
	h2_list.append(h2.get_text())
	
for h3 in soup.find_all("h3"):
	h3_list.append(h3.get_text())
	
# import pdb
# pdb.set_trace()

text = p_list + h2_list + h3_list

documents = '.'.join(str(x) for x in text)

credential = AzureKeyCredential("188fe77ba5e440e9bef0a01842e6e38e")
endpoint="https://hacklanguage.cognitiveservices.azure.com/"

text_analytics_client = TextAnalyticsClient(endpoint, credential)

# documents = [
#     """
#     Microsoft was founded by Bill Gates and Paul Allen. Its headquarters are located in Redmond. Redmond is a
#     city in King County, Washington, United States, located 15 miles east of Seattle.
#     """,
#     "Jeff bought three dozen eggs because there was a 50% discount."
# ]

# documents = [
# 	"In the last year, geopolitical tension has led to an uptick of reported cybercrime events fueled by hacktivist groups"]


sent_text = nltk.sent_tokenize(documents) # this gives us a list of sentences
# now loop over each sentence and tokenize it separately
# start_pos = []
# end_pos = []
def get_relation(sent):

    doc = nlp(sent)

    # Matcher class object 
    matcher = Matcher(nlp.vocab)

    #define the pattern 
    pattern = [{'DEP':'ROOT'}, 
            {'DEP':'prep','OP':"?"},
            {'DEP':'agent','OP':"?"},  
            {'POS':'ADJ','OP':"?"}] 

    # matcher.add("matching_1", None, pattern) 
    matcher.add("matching_1", [pattern])

    matches = matcher(doc)
    k = len(matches) - 1

    span = doc[matches[k][1]:matches[k][2]]


    start_pos = sent.find(span.text)
    # end_pos = matches[k][2]
    # import pdb
    # pdb.set_trace()

    return(span.text, start_pos)


entities_df = []
etext_list = []
ecategory_list = []
econfi_score_list = []
eoffset_list = []
idx_list = []

for idx, sentence in enumerate(sent_text):
    _sentence = [sentence]
    response = text_analytics_client.recognize_entities(_sentence, language="en")
    result = [doc for doc in response if not doc.is_error]

    for doc in result:
        for entity in doc.entities:
            # import pdb
            # pdb.set_trace()
            # entities.append(entity)
            print(f"Entity: {entity.text}")
            etext_list.append(entity.text)
            print(f"...Category: {entity.category}")
            ecategory_list.append(entity.category)
            print(f"...Confidence Score: {entity.confidence_score}")
            econfi_score_list.append(entity.confidence_score)
            print(f"...Offset: {entity.offset}")
            eoffset_list.append(entity.offset)
            idx_list.append(idx)


entities_df = pd.DataFrame(list(zip(idx_list, etext_list, ecategory_list, econfi_score_list, eoffset_list))).reset_index(drop=True)
entities_df.columns = ['idx', 'entity', 'entity_category', 'entity_score', 'entity_offset']

entity_to_filter = ['DateTime', 'Quantity']

threat_entities_df = entities_df[entities_df['entity_category'].isin(entity_to_filter)]

relations = [[idx, get_relation(sentence)] for idx, sentence in enumerate(sent_text)]

import pdb
pdb.set_trace()

