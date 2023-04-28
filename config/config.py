# Configuration for web scraping
words2check = ["trendmicro.com/en_us/research", "microsoft.com/en-us/security/blog/2023", "threat-intel-research", "blogs/threat-intelligence"]
existing_urls_path = 'data/input/articles_urls.txt'
main_urls_path = 'data/input/urls.txt'

# Entities to keep and special chars
en_to_keep = ['DateTime', 'Event', 'PersonType', 'Organization', 'Location', 'Product', 'Person']
special_chars = ["*", "/", "&"]

# Threshold to match subject and entity
sub_match_thresh = 30

# Chunk size to insert into Database
chunk_size = 100
urls_limit = 1

# Save_log
save_log='logs'
log_to_file='logs.txt'                                                      
log_level='debug'
