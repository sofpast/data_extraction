# Introduction 
The project provides a solution for the `problem 1 BAE System`, which is create a knowledge graph to represent `threat actors` entitiesextracted from online intelligent security blogs/ articles and the relationship between them. The knowledge graph is stored in a graph database named `threatactor-database`.

The project includes four main steps:
1. Scrape data from articles by using `Beautifulsoup`
2. Extract entities from extracted paragraphs by using `Azure Text Analytics Prebuilt Model`
3. Extract relations between pairs of two entities by using triple extraction from `Stanford Openie`
4. Build knowledge by using `Gremlin` queries and storing the vertex and edges into `Azure Cosmos DB`

Project Structure
---------------------------------
```text
data_extraction/
│
├── config/                                     <- Configuration
│   ├── __init__.py
│   └── config.py                               <- Configuration file
│
├── data/                                       <- Data folder
│   ├── input/                                  <- Input data folder
│   │   ├── articles_urls.txt                   <- Articles' urls to scrape
│   │   └── urls.txt                            <- Contain 4 main urls to crawl data automatically
│
├── samples/                                    <- Knowledge graph samples
│   └── kb.PNG                                  <- Knowledge graph outputed from the program
│
├── .env                                        <- Store credentials to access Azure services
├── .gitignore
├── execute_pipeline.py                         <- Execute main pipeline
├── knowledge_graph.py                          <- Knowledge graph queries
├── logger.py                                   <- Define logger
├── README.md                                   <- README for inference
├── relation_extractor.py                       <- Entities and relation extraction
├── requirements.txt                            <- Package requirements
├── run.sh                                      <- Run command for reference
└── web_scrape.py                               <- Web scraping
```

# Getting Started

## Package requirement
>- python==3.8.16
>- azure-ai-textanalytics==5.2.1
>- gremlinpython==3.4.13
>- spacy==3.5.1
>- stanford_openie==1.3.1

## Installation process
First, create an Anaconda environment then install the environment by using `requirements.txt` and other packages as the commands below.

1. Create new environement
```bash
conda create --name hackathon python==3.8.16
```
Activate the environement
```bash
conda activate hackathon
```
2. Install requirements
```bash
pip install -r requirements.txt
```
3. Install other packages

Besides packages listed in `requirement.txt`, `spacy` is required for some step in tokenizing the documents into sentences. To install spacy, use the command below:

* Install spacy
```bash
pip install -U pip setuptools wheel
pip install -U spacy
python -m spacy download en_core_web_sm
```
* Install stanford_openie
`stanford_openie` is used to extract a triple (subject-verb-object) from a sentence, this is an important step to find the relation between two entities. The installation of stanford_openie could be done by using `pip install stanford_openie` or with the certain version specified in `requirement.txt`. One thing to notice that it requires Java JDK installed in your computer.

To check and install JDK version, please access to the link: [Download JDK](https://www.oracle.com/java/technologies/downloads/)

## Setup parameters
### For `.env` file
In the `.env`, you need to replace your own services key, credentials to access to `Azure Text Analytics` and `Cosmos DB`.

```
# Credentials to language services
LANGUAGE_SERVICE_KEY = "YOUR_LANGUAGE_SERVICE_KEY"
LANGUAGE_SERVICE_ENDPOINT = "YOUR_LANGUAGE_SERVICE_ENDPOINT"

# CosmosDB
COSMOSDB_WWS = "YOUR_COSMOSDB_WWS"
COSMOSDB_USERNAME = "YOUR_COSMOSDB_USERNAME"
COSMOSDB_PASSWORD = "YOUR_COSMOSDB_PASSWORD"
```
### For `config.py` file
>+ existing_urls_path: urls_path already stored in .txt file
>+ main_urls_path: path contains 4 main URLs, from there the program will extract the detail URLs/ article links automatically. 
>+ en_to_keep: Azure TexAnalytics extracts many types of entities, these parameters will help to restrict some basic entity types related to `threat actor` for further analysis. 
>+ special_chars: special characters to be removed
>+ sub_match_thresh: threshold to map subject extracted from `stanford_openie` and entities
>+ chunk_size: size to divide a list of insert queries into chunks of 100 elements to avoid burdening the database
>+ urls_limit: limit the number of URLs to run scraping and analysis to avoid being blocked by autobot detection


# Run the pipeline
Use the command below to run the the pipeline
```bash
# Run with default mode auto_scrape_urls 
python execute_pipeline.py
# Run with mode urls_from_txt
python execute_pipeline.py --mode urls_from_txt
# Run with drop the existing graph before inserting new
python execute_pipeline.py --drop_graph
```
*Input arguments*
+ `--mode`: type=str, default="auto_scrape_urls", help="Run mode (urls_from_txt/auto_scrape_urls)"
+ `--drop_graph`: action='store_true', help="Drop existing graph before inserting"

This will trigger from scaping blog/ articles' contents that are specified in `data/input/articles_urls.txt`, then extract entities and relations until preparing Gremlin queries for `_gremlin_insert_verties` and `_gremlin_insert_edges` into the Cosmos DB. if sucessfully, the terminal will display number of vertices and edges to insert into Cosmos DB as below:
```
2023-04-26 13:43:07,897: INFO: Extracting en_rel for url: https://symantec-enterprise-blogs.security.com/blogs/threat-intelligence/xtrader-3cx-supply-chain
2023-04-26 13:43:07,899: INFO: Extracted entities_df shape: 106 | triple_df shape: 542
2023-04-26 13:43:08,064: INFO: en_rel_df shape: 23
2023-04-26 13:43:27,537: INFO: Extracting en_rel for url: https://www.crowdstrike.com/blog/crowdstrike-detects-and-prevents-active-intrusion-campaign-targeting-3cxdesktopapp-customers/
2023-04-26 13:43:27,538: INFO: Extracted entities_df shape: 118 | triple_df shape: 309
2023-04-26 13:43:27,701: INFO: en_rel_df shape: 14
2023-04-26 13:43:27,818: INFO: Connect to Azure Cosmos DB + Gremlin successfully
2023-04-26 13:43:30,217: INFO: Number of vertices to insert into the graph: 86
2023-04-26 13:43:30,922: INFO: Number of edges to insert into the graph: 37
2023-04-26 13:43:30,922: INFO: Count number of vertices in the graph
```
You can query data by using Gremlin or query by interacting in UI. The output will look as below:
<img src="samples/kb.png" width="800" height="400">

# Solution Architectures
TO be updated

