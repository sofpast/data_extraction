# Credentials to language services
LANGUAGE_SERVICE_KEY = '188fe77ba5e440e9bef0a01842e6e38e'
LANGUAGE_SERVICE_ENDPOINT = "https://hacklanguage.cognitiveservices.azure.com/"

# Configuration for web scraping
words2check = ["trendmicro.com/en_us/research", "microsoft.com/en-us/security/blog/2023", "threat-intel-research", "blogs/threat-intelligence"]
existing_urls_path = 'data/articles_urls.txt'
main_urls_path = 'data/urls.txt'

# other words
en_to_keep = ['DateTime', 'Event', 'PersonType', 'Organization', 'Location', 'Product', 'Person']
remove_list = ["*", "/", "&"]