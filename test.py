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
# import nltk
nltk.download('punkt')

import spacy
import numpy as np
# from spacy import displaycy

nlp = spacy.load('en_core_web_sm')

from spacy.matcher import Matcher 
from spacy.tokens import Span 
import tqdm

import bisect
import math

# from __future__ import unicode_literals, print_function
from spacy.lang.en import English 

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
	
# for h3 in soup.find_all("h3"):
# 	h3_list.append(h3.get_text())
	
# import pdb
# pdb.set_trace()
text = p_list
# text = p_list + h2_list + h3_list

documents = ''.join(str(x) for x in text)

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


# sent_text = nltk.sent_tokenize(documents) # this gives us a list of sentences

nlp = spacy.load('en_core_web_sm')
# nlp.add_pipe(nlp.create_pipe('sentencizer')) # updated
# doc = nlp(documents)
sent_text = [i for i in nlp(documents).sents]

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
    # import pdb
    # pdb.set_trace()
    _sentence = [str(sentence)]
    response = text_analytics_client.recognize_entities(_sentence, language="en")
    result = [doc for doc in response if not doc.is_error]

    for doc in result:
        for entity in doc.entities:
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
entities_df['has_rel'] = ""
entities_df['is_source'] = ""

# entity_to_filter = ['DateTime', 'Quantity']

# threat_entities_df = entities_df[~entities_df['entity_category'].isin(entity_to_filter)]

relations = [[idx, get_relation(str(sentence))] for idx, sentence in enumerate(sent_text)]
relations_df = pd.DataFrame(relations).reset_index(drop=True)
relations_df.columns = ['idx', 'relations']
relations_df[['relation', 'offset']] = pd.DataFrame(relations_df['relations'].tolist(), index=relations_df.index)



# for idx, row in relations_df.iterrows(): 
#     print(row)
#     re_offset 

def get_lower_bound(haystack, needle):
    start_idx = bisect.bisect(haystack, needle)
    # print(row)
    # import pdb
    # pdb.set_trace()
    if 0 < start_idx < len(haystack):
        return start_idx-1
    else:
        # raise ValueError(f"{needle} is out of bounds of {haystack}")
        # pass
        return np.nan

for id, row in relations_df.iterrows():

    print(row)
    sub = entities_df[entities_df['idx']==id].reset_index(drop=True)
    start_idx = get_lower_bound(sub.entity_offset.tolist(), row['offset'])
    if math.isnan(start_idx) is False:
        print(f"{id} -- it is not NaN")      
        sub_olist = sub.loc[start_idx: start_idx+1, 'entity_offset'].tolist()
        entities_df.loc[(entities_df['idx']==id)& (entities_df.entity_offset == sub_olist[0]), 'is_source'] = "Y"
        entities_df.loc[(entities_df['idx']==id) & (entities_df['entity_offset'].isin(sub_olist)), 'has_rel'] = id
    else:
         continue

import pdb
pdb.set_trace()
     


