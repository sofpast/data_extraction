from openie import StanfordOpenIE

# https://stanfordnlp.github.io/CoreNLP/openie.html#api
# Default value of openie.affinity_probability_cap was 1/3.

import pandas as pd
import spacy
from web_scrape import *
from bs4 import BeautifulSoup
import requests

# url = "https://www.microsoft.com/en-us/security/blog/2023/03/17/killnet-and-affiliate-hacktivist-groups-targeting-healthcare-with-ddos-attacks/"
# url = "https://www.microsoft.com/en-us/security/blog/2023/04/07/mercury-and-dev-1084-destructive-attack-on-hybrid-environment/"

url = "https://en.wikipedia.org/wiki/Russian_Empire"

nlp = spacy.load('en_core_web_sm')

htmldata = getdata(url)
soup = BeautifulSoup(htmldata, 'html.parser')
text = []

for para in soup.find_all("p"):
    print(para.get_text())
    text.append(para.get_text())
documents = ''.join(str(x) for x in text)
# import pdb
# pdb.set_trace()
sent_text = [i for i in nlp(documents).sents]
# sent_text = scrape_web(url, nlp)

properties = {
    'openie.affinity_probability_cap': 2 / 3,
}

with StanfordOpenIE(properties=properties) as client:
    # text = 'Barack Obama was born in Hawaii. Richard Manning wrote this sentence.'

    text = str(sent_text[0])
    print('Text: %s.' % text)
    for triple in client.annotate(text):
        print('|-', triple)

    # graph_image = 'graph.png'
    # client.generate_graphviz_graph(text, graph_image)
    # print('Graph generated: %s.' % graph_image)

    # with open('corpus/pg6130.txt', encoding='utf8') as r:
    #     corpus = r.read().replace('\n', ' ').replace('\r', '')

    # triples_corpus = client.annotate(corpus[0:5000])
    # print('Corpus: %s [...].' % corpus[0:80])
    # print('Found %s triples in the corpus.' % len(triples_corpus))
    # for triple in triples_corpus[:3]:
    #     print('|-', triple)
    # print('[...]')