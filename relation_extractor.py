import csv
import os
import os.path
import time

import nltk
import pandas as pd
import requests
from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.credentials import AzureKeyCredential
from bs4 import BeautifulSoup
from dotenv import load_dotenv

import bisect
import math

import numpy as np
import spacy
import tqdm
from spacy.lang.en import English
from spacy.matcher import Matcher
from spacy.tokens import Span

from web_scrape import *
from config import config
from openie import StanfordOpenIE


def get_relation(sent, nlp):
    doc = nlp(sent)
    
    # Matcher class object 
    matcher = Matcher(nlp.vocab)

    #define the pattern 
    pattern = [{'DEP':'ROOT'}, 
            {'DEP':'prep','OP':"?"},
            {'DEP':'agent','OP':"?"},  
            {'POS':'ADJ','OP':"?"}] 

    matcher.add("matching_1", [pattern])
    matches = matcher(doc)
    k = len(matches) - 1
    span = doc[matches[k][1]:matches[k][2]]
    start_pos = sent.find(span.text)

    return(span.text, start_pos)

def get_lower_bound(haystack, needle):
    start_idx = bisect.bisect(haystack, needle)

    if 0 < start_idx < len(haystack):
        return start_idx-1
    else:
        return np.nan

def extract_entity(sent_text):
    try:
        credential = AzureKeyCredential(config.LANGUAGE_SERVICE_KEY)
        endpoint = config.LANGUAGE_SERVICE_ENDPOINT
        text_analytics_client = TextAnalyticsClient(endpoint, credential)

        entities_df = []
        etext_list = []
        ecategory_list = []
        econfi_score_list = []
        eoffset_list = []
        idx_list = []

        for idx, sentence in enumerate(sent_text):
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
    
    except Exception as ex:
        print(ex)

    return entities_df

def merge_en_rel(entities_df, relations_df):
    # Merged entities and relations
    for id, row in relations_df.iterrows():
        sub = entities_df[entities_df['idx']==id].reset_index(drop=True)
        start_idx = get_lower_bound(sub.entity_offset.tolist(), row['offset'])
        if math.isnan(start_idx) is False:
            print(f"{id} -- it is not NaN")      
            sub_olist = sub.loc[start_idx: start_idx+1, 'entity_offset'].tolist()
            entities_df.loc[(entities_df['idx']==id)& (entities_df.entity_offset == sub_olist[0]), 'is_source'] = "Y"
            entities_df.loc[(entities_df['idx']==id) & (entities_df['entity_offset'].isin(sub_olist)), 'has_rel'] = id
        else:
            continue
    
    return entities_df, relations_df

def remove_char(remove_list, text):
    for char in remove_list:
        text = text.replace(char, "")
    return text

def find_subjects(parsed_text):
    subject_list = []
    object_list = []
    #get token dependencies
    for text in parsed_text:
        #subject would be
        if text.dep_ == "nsubj":
            subject = text.orth_
            subject_list.append(subject)
            print(f"subject: {subject}")
        #iobj for indirect object
        if text.dep_ == "iobj":
            indirect_object = text.orth_
            print(f"indirect object: {indirect_object}")
        #dobj for direct object
        if text.dep_ == "dobj":
            direct_object = text.orth_
            print(f"direct object: {direct_object}")
            object_list.append(direct_object)
    return subject_list, object_list

def get_triple(sent_text):
    triple_list = []
    triple_df = pd.DataFrame()
    properties = {'openie.affinity_probability_cap': 2 / 3,}

    with StanfordOpenIE(properties=properties) as client:
        for idx, sent in enumerate(sent_text):
            sub_triple = []
            text = str(sent)
            print('Text: %s.' % text)
            for triple in client.annotate(text):
                print('|-', triple)
                sub_triple.append(triple)
            triple_list.append(sub_triple)

    for idx, sub in enumerate(triple_list):
        df = pd.DataFrame(sub)
        df['idx'] = idx
        triple_df = pd.concat([triple_df, df], ignore_index=True, sort=False)

    # triple_df.groupby('idx', as_index=False).agg({'subject': lambda x: x.tolist(), 'relation': lambda x: x.tolist(), 'object': lambda x: x.tolist()})

    return triple_df