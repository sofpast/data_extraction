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
from config import config


# link for extract html data
def getdata(url, headers):
	r = requests.get(url, headers)
	return r.text

def scrape_web(url, nlp, headers):
    htmldata = getdata(url, headers)
    soup = BeautifulSoup(htmldata, 'html.parser')
    text = []

    for para in soup.find_all("p"):
        print(para.get_text())
        text.append(para.get_text())

    documents = ''.join(str(x) for x in text)
    sent_text = [i for i in nlp(documents).sents]

    return sent_text

def get_new_urls(existing_urls_path, main_urls_path, words2check):
    existing_urls = []
    new_urls = []

    with open(existing_urls_path, 'r') as urls_file:
        for line in urls_file:
            existing_urls.append(line.strip())

    with open(existing_urls_path, "a+") as f:
        with open (main_urls_path, 'r') as main_urls:
            for line in main_urls:
                urls = line.strip()
                print(f"--------start check url:{urls}--------")
                grab = requests.get(urls)
                soup = BeautifulSoup(grab.text, 'html.parser') #

                for link in soup.find_all("a"):
                    data = link.get('href')                    
                    if data not in existing_urls and data not in new_urls and data is not None:           
                        if any(word in data for word in words2check) and data.startswith("https:"):
                            print(data)
                            new_urls.append(data)
                            f.write(data)
                            f.write("\n")
                        elif any(word in data for word in words2check) and "trendmicro" in data:
                            data = urls + "/" + data.split("/")[-1]
                            new_urls.append(data)
                            f.write(data)
                            f.write("\n")
                    else:
                        continue            
        f.close()
    
    return new_urls

if __name__ == "__main__":
    words2check = config.words2check
    main_urls_path = config.main_urls_path
    existing_urls_path = config.existing_urls_path
    
    new_urls = get_new_urls(existing_urls_path
                            , main_urls_path, words2check)
    print(new_urls)