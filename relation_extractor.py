import bisect
import math

import numpy as np
import pandas as pd
import requests
import spacy
from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.credentials import AzureKeyCredential
from bs4 import BeautifulSoup
from openie import StanfordOpenIE
from spacy.lang.en import English
from spacy.matcher import Matcher
from spacy.tokens import Span
from thefuzz import fuzz, process
from dotenv import load_dotenv
import os

from config import config
from web_scrape import *


def get_relation(sent, nlp):
    """
    extract relation by using spacy Matcher
    """
    doc = nlp(sent)
    # Matcher class object
    matcher = Matcher(nlp.vocab)
    # define the pattern
    pattern = [{'DEP': 'ROOT'},
               {'DEP': 'prep', 'OP': "?"},
               {'DEP': 'agent', 'OP': "?"},
               {'POS': 'ADJ', 'OP': "?"}]

    matcher.add("matching_1", [pattern])
    matches = matcher(doc)
    k = len(matches) - 1
    span = doc[matches[k][1]:matches[k][2]]
    start_pos = sent.find(span.text)

    return (span.text, start_pos)


def get_lower_bound(haystack, needle):
    start_idx = bisect.bisect(haystack, needle)
    if 0 < start_idx < len(haystack):
        return start_idx-1
    else:
        return np.nan


def extract_entity(sent_text):
    try:
        load_dotenv()
        # credential = AzureKeyCredential(config.LANGUAGE_SERVICE_KEY)
        credential = AzureKeyCredential(os.getenv("LANGUAGE_SERVICE_KEY"))
        # endpoint = config.LANGUAGE_SERVICE_ENDPOINT
        endpoint = os.getenv("LANGUAGE_SERVICE_ENDPOINT")
        text_analytics_client = TextAnalyticsClient(endpoint, credential)

        entities_df = []
        etext_list = []
        ecategory_list = []
        econfi_score_list = []
        eoffset_list = []
        idx_list = []

        for idx, sentence in enumerate(sent_text):
            _sentence = [str(sentence)]
            response = text_analytics_client.recognize_entities(
                _sentence, language="en")
            result = [doc for doc in response if not doc.is_error]

            for doc in result:
                for entity in doc.entities:
                    etext_list.append(entity.text)
                    ecategory_list.append(entity.category)
                    econfi_score_list.append(entity.confidence_score)
                    eoffset_list.append(entity.offset)
                    idx_list.append(idx)

        entities_df = pd.DataFrame(list(zip(
            idx_list, etext_list, ecategory_list, econfi_score_list, eoffset_list))).reset_index(drop=True)
        entities_df.columns = ['idx', 'entity',
                               'entity_category', 'entity_score', 'entity_offset']

    except Exception as ex:
        print(ex)

    return entities_df


def remove_char(remove_list, text):
    for char in remove_list:
        text = text.replace(char, "")
    return text


def find_subjects(parsed_text):
    subject_list = []
    object_list = []
    # get token dependencies
    for text in parsed_text:
        # subject would be
        if text.dep_ == "nsubj":
            subject = text.orth_
            subject_list.append(subject)
        # dobj for direct object
        if text.dep_ == "dobj":
            direct_object = text.orth_
            object_list.append(direct_object)
    return subject_list, object_list


def get_triple(sent_text):
    """get triple by using stanford_openie
    """
    triple_list = []
    triple_df = pd.DataFrame()
    properties = {'openie.affinity_probability_cap': 2 / 3, }

    with StanfordOpenIE(properties=properties) as client:
        for idx, sent in enumerate(sent_text):
            sub_triple = []
            text = str(sent)
            # print('Text: %s.' % text)
            for triple in client.annotate(text):
                # print('|-', triple)
                sub_triple.append(triple)
            triple_list.append(sub_triple)

    for idx, sub in enumerate(triple_list):
        df = pd.DataFrame(sub)
        df['idx'] = idx
        triple_df = pd.concat([triple_df, df], ignore_index=True, sort=False)

    return triple_df


def similarity_text(text1, text2):
    res = fuzz.ratio(str(text1), str(text2))
    return res
