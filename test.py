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

# import nltk
# nltk.download('punkt')

import bisect
import math

import numpy as np
import spacy
import tqdm
from spacy.lang.en import English
from spacy.matcher import Matcher
from spacy.tokens import Span

from web_scrape import *
from relation_extractor import *
from config import config

nlp = spacy.load('en_core_web_sm')

merged_df = pd.DataFrame()

with open ('data/articles_urls.text', 'r') as url_file:
    for line in url_file:

        url = line.strip()
        sent_text = scrape_web(url, nlp)

        entities_df = extract_entity(sent_text)
        entities_df[['has_rel', 'is_source']] = ""

        # If need to filder some entity types
        # entity_to_filter = ['DateTime', 'Quantity']
        # entities_df = entities_df[~entities_df['entity_category'].isin(entity_to_filter)]

        relations = [[idx, get_relation(str(sentence), nlp)] for idx, sentence in enumerate(sent_text)]
        relations_df = pd.DataFrame(relations, columns=['has_rel', 'relations']).reset_index(drop=True)
        relations_df[['relation', 'offset']] = pd.DataFrame(relations_df['relations'].tolist(), index=relations_df.index)

        entities_df, relations_df = merge_en_rel(entities_df, relations_df)


        merged_df = pd.concat([merged_df, entities_df.merge(relations_df, on='has_rel', how='left')], ignore_index=True, sort=False)


import pdb
pdb.set_trace()

    


