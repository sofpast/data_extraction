from openie import StanfordOpenIE

# https://stanfordnlp.github.io/CoreNLP/openie.html#api
# Default value of openie.affinity_probability_cap was 1/3.

import pandas as pd
import spacy
from web_scrape import *
from bs4 import BeautifulSoup
import requests

from fake_useragent import UserAgent
# import requests
   
# url = "https://www.microsoft.com/en-us/security/blog/2023/03/17/killnet-and-affiliate-hacktivist-groups-targeting-healthcare-with-ddos-attacks/"
# url = "https://www.microsoft.com/en-us/security/blog/2023/04/07/mercury-and-dev-1084-destructive-attack-on-hybrid-environment/"

# url = "https://www.microsoft.com/en-us/security/blog/2023/04/06/devops-threat-matrix/"
# url = "https://www.microsoft.com/en-us/security/blog/2021/02/18/forrester-consulting-tei-study-azure-security-center-delivers-219-percent-roi-over-3-years-and-a-payback-of-less-than-6-months/"
url = "https://en.wikipedia.org/wiki/Knowledge_graph#:~:text=Knowledge%20graphs%20are%20often%20used,semantics%20underlying%20the%20used%20terminology."


nlp = spacy.load('en_core_web_sm')

# htmldata = getdata(url)
# headers = {
#     'User-Agent': 'My User Agent 1.0',
#     'From': 'pjamjin@gmail.com'  # This is another valid field
# }
ua = UserAgent()
print(ua.chrome)
headers = {'User-Agent':str(ua.chrome)}
print(headers)

# headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36'}

htmldata = getdata(url, headers=headers)

# response = requests.get(url, headers=headers)

soup = BeautifulSoup(htmldata, 'html.parser')
text = []

for para in soup.find_all("p"):
    print(para.get_text())
    text.append(para.get_text())
documents = ''.join(str(x) for x in text)
import pdb
pdb.set_trace()
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