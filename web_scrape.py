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


# link for extract html data
def getdata(url):
	r = requests.get(url)
	return r.text

def scrape_web(url, nlp):
    htmldata = getdata(url)
    soup = BeautifulSoup(htmldata, 'html.parser')
    text = []

    for para in soup.find_all("p"):
        print(para.get_text())
        text.append(para.get_text())

    documents = ''.join(str(x) for x in text)
    sent_text = [i for i in nlp(documents).sents]

    return sent_text

