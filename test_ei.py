from openie import StanfordOpenIE

# https://stanfordnlp.github.io/CoreNLP/openie.html#api
# Default value of openie.affinity_probability_cap was 1/3.

import pandas as pd
import spacy
from web_scrape import *
from bs4 import BeautifulSoup
import requests

from fake_useragent import UserAgent


nlp = spacy.load('en_core_web_sm')

sentences = []
sent_text = []
with open('data/tmp/sent_text.txt', 'r') as f:
    for line in f:
        sentences.append(line.strip())
# nlp = spacy.load('en_core_web_sm')
documents = ''.join(str(x) for x in sentences)
sent_text = [i for i in nlp(documents).sents]

properties = {
    'openie.affinity_probability_cap': 2 / 3,
}
# triple_list = []
# with StanfordOpenIE(properties=properties) as client:
#     # text = 'Barack Obama was born in Hawaii. Richard Manning wrote this sentence.'
#     for idx, sent in enumerate(sent_text):
#         sub_triple = []
#         text = str(sent)
#         print('Text: %s.' % text)
#         for triple in client.annotate(text):
#             print('|-', triple)
#             sub_triple.append(triple)
#         triple_list.append(sub_triple)

# triple_df = pd.DataFrame()
# for idx, sub in enumerate(triple_list):
#     df = pd.DataFrame(sub)
#     df['idx'] = idx
#     triple_df = pd.concat([triple_df, df], ignore_index=True, sort=False)

# triple_df.groupby('idx', as_index=False).agg({'subject': lambda x: x.tolist(), 'relation': lambda x: x.tolist(), 'object': lambda x: x.tolist()})

triple_df = pd.read_pickle('data/tmp/triple_df.pkl')
entities_df = pd.read_pickle('data/tmp/entities_df.pkl')
entities_df['subject'] = entities_df['entity']
subject_df = pd.merge(entities_df, triple_df, how='left', on =['idx', 'subject'])
idx_lst = subject_df[~subject_df.relation.isnull()]['idx'].unique().tolist()


def find_objects(text, en_lst):
    en_obj_lst = []
    for en in en_lst:
        if en in text:
            en_obj_lst.append(en)
    # en_obj_lst = [en if en in text for en in en_lst]  
    return en_obj_lst
en_rel_df = pd.DataFrame()
for idx in idx_lst:
    sub = subject_df[subject_df.idx==idx]
    en_lst = sub[sub['relation'].isnull()]['entity'].tolist()
    sub['en_obj'] = sub['object'].astype(str).apply(lambda x: find_objects(x, en_lst))
    en_rel_df = pd.concat([en_rel_df, sub])
en_rel_df = en_rel_df[(~en_rel_df.relation.isnull())&(en_rel_df['en_obj'].str.len()!=0)][['idx','subject', 'relation', 'en_obj']] 
en_rel_df = en_rel_df.explode('en_obj').drop_duplicates().reset_index(drop=True)


import pdb
pdb.set_trace()
