import requests
from bs4 import BeautifulSoup
from web_scrape import *

existing_urls = []
new_urls = []
words2check = ["trendmicro.com/en_us/research", "microsoft.com/en-us/security/blog/2023/04"]

with open('data/articles_urls.txt', 'r') as urls_file:
    for line in urls_file:
        existing_urls.append(line.strip())

with open("data/articles_urls.txt", "a+") as f:
    with open ('data/urls.txt', 'r') as main_urls:
        for line in main_urls:
            urls = line.strip()
            print(f"***start check url:{urls}")

            grab = requests.get(urls)
            soup = BeautifulSoup(grab.text, 'html.parser')

            for link in soup.find_all("a"):
                data = link.get('href')
                print(data)
                if data not in existing_urls and data is not None:                    
                    if data.startswith("https:") and any(word in data for word in words2check): 
                        new_urls.append(data)
                        # f.write(data)
                        # f.write("\n")
                else:
                    continue
    f.close()
