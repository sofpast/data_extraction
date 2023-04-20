# Credentials to language services
LANGUAGE_SERVICE_KEY = "YOUR_LANGUAGE_SERVICE_KEY"
LANGUAGE_SERVICE_ENDPOINT = "YOUR_LANGUAGE_SERVICE_ENDPOINT"

# CosmosDB
COSMOSDB_WWS = "YOUR_COSMOSDB_WWS"
COSMOSDB_USERNAME = "YOUR_COSMOSDB_USERNAME"
COSMOSDB_PASSWORD= "YOUR_COSMOSDB_PASSWORD"

# Configuration for web scraping
words2check = ["trendmicro.com/en_us/research", "microsoft.com/en-us/security/blog/2023", "threat-intel-research", "blogs/threat-intelligence"]
existing_urls_path = 'data/input/articles_urls.txt'
main_urls_path = 'data/input/urls.txt'

# other words
en_to_keep = ['DateTime', 'Event', 'PersonType', 'Organization', 'Location', 'Product', 'Person']
special_chars = ["*", "/", "&"]
