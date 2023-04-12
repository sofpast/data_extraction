import requests
from bs4 import BeautifulSoup
from web_scrape import *

existing_url = []
new_urls = []

with open('data/articles_urls.txt', 'r') as urls_file:
    for line in urls_file:
        existing_url.append(line.strip())

with open("data/articles_urls.txt", "a+") as f:
    with open ('data/urls.txt', 'r') as main_urls:
        for line in main_urls:
            urls = line.strip()

            grab = requests.get(urls)
            soup = BeautifulSoup(grab.text, 'html.parser')

            for link in soup.find_all("a"):
                data = link.get('href')

                if data not in existing_url and data is not None:
                    
                    if data.startswith("https:"): 
                        new_urls.append(data)
                        f.write(data)
                        f.write("\n")
                else:
                    continue
    f.close()
