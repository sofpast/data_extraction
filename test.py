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
from relation_extractor import *
from config import config
from fake_useragent import UserAgent

nlp = spacy.load('en_core_web_sm')

words2check = config.words2check
main_urls_path = config.main_urls_path
existing_urls_path = config.existing_urls_path
en_to_keep = config.en_to_keep

ua = UserAgent()
print(ua.chrome)
headers = {'User-Agent':str(ua.chrome)}
print(headers)

if __name__ == "__main__":
    merged_df = pd.DataFrame()   
    # new_urls = get_new_urls(existing_urls_path
    #                         , main_urls_path, words2check)
    new_urls = ["https://symantec-enterprise-blogs.security.com/blogs/threat-intelligence/mantis-palestinian-attacks"]

    if len(new_urls) > 0:
        for line in new_urls:
            # url = line.strip()
            url = line
            sent_text = scrape_web(url, nlp, headers)
            with open('data/tmp/sent_text.txt', 'w') as f:
                for line in sent_text:
                    f.write(f"{line}\n")
            import pdb
            pdb.set_trace()
            # Extract entities
            entities_df = extract_entity(sent_text)
            entities_df[['has_rel', 'is_source']] = ""
            entities_df = entities_df[entities_df['entity_category'].isin(en_to_keep)]
            # Extract relations
            relations = [[idx, get_relation(str(sentence), nlp)] for idx, sentence in enumerate(sent_text)]
            relations_df = pd.DataFrame(relations, columns=['has_rel', 'relations']).reset_index(drop=True)
            relations_df[['relation', 'offset']] = pd.DataFrame(relations_df['relations'].tolist(), index=relations_df.index)
            entities_df, relations_df = merge_en_rel(entities_df, relations_df)
            merged_df = pd.concat([merged_df, entities_df.merge(relations_df, on='has_rel', how='left')], ignore_index=True, sort=False)

        merged_df.to_pickle('data/new_merged_df.pkl')

    


