# Credentials to language services
LANGUAGE_SERVICE_KEY = '188fe77ba5e440e9bef0a01842e6e38e'
LANGUAGE_SERVICE_ENDPOINT = "https://hacklanguage.cognitiveservices.azure.com/"

# CosmosDB
COSMOSDB_WWS = "wss://cosmosdbhack.gremlin.cosmos.azure.com:443/"
COSMOSDB_USERNAME = "/dbs/threatactor-database/colls/threatactor-graph"
COSMOSDB_PASSWORD= "SHwb6lPjs2CzVvyFxp8bpALcY3oQQ2d7l9s9ydRCwtWJ7ywg5zP0Ka3Gl2LgGm4yYuR11JxNxYg9ACDbQfOMeg=="

# Configuration for web scraping
words2check = ["trendmicro.com/en_us/research", "microsoft.com/en-us/security/blog/2023", "threat-intel-research", "blogs/threat-intelligence"]
existing_urls_path = 'data/input/articles_urls.txt'
main_urls_path = 'data/input/urls.txt'

# other words
en_to_keep = ['DateTime', 'Event', 'PersonType', 'Organization', 'Location', 'Product', 'Person']
special_chars = ["*", "/", "&"]
