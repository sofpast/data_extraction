# Introduction 
The project aims to create a database named `threat-actor` to represent the interconnection among `threat actors` from information extracted from online intelligent security blogs/ articles.

* A solution for BAE Systems problem 1

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
├── .gitignore
├── README.md                                   <- README for inference
├── execute_pipeline.py                         <- Execute main pipeline
├── knowledge_graph.py                          <- Knowledge graph queries
├── relation_extractor.py                       <- Entities and relation extraction
├── requirements.txt                            <- Package requirements
├── test.py                                     <- Testing (Implementing)
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

# Run the pipeline
1. First, in the `config.py`, you need to replace your own services key, credentials to access to `Azure Text Analytics` and `Cosmos DB`.

```
# Credentials to language services
LANGUAGE_SERVICE_KEY = YOUR_LANGUAGE_SERVICE_KEY
LANGUAGE_SERVICE_ENDPOINT = YOUR_LANGUAGE_SERVICE_ENDPOINT

# CosmosDB
COSMOSDB_WWS = YOUR_COSMOSDB_WWS
COSMOSDB_USERNAME = YOUR_COSMOSDB_USERNAME
COSMOSDB_PASSWORD = YOUR_COSMOSDB_PASSWORD
```

2. Second, use the command below to run the the pipeline
```bash
python execute_pipeline.py
```

This will trigger from scaping blog/ articles' contents that are specified in `data/input/articles_urls.txt`, then extract entities and relations until preparing Gremlin queries for `_gremlin_insert_verties` and `_gremlin_insert_edges` into the Cosmos DB. if sucessfully, the terminal will display number of vertices and edges to insert into Cosmos DB as below:
```
Connect to Azure Cosmos DB + Gremlin on Python!
Drop graph is on the server...
Number of vertices to insert into the graph: 46
Number of edges to insert into the graph: 4
        Count of vertices: [135]
```
You can query data by using Gremlin or query by interacting in UI. The output will look as below:
<img src="samples/kb.png" width="800" height="400">

# Solution Architectures
TO be updated

