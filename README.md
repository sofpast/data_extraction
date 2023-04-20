# Introduction 
The project aims to create a database called `threat-actor` to represent the interconnection among `threat actors` from information extracted from intelligent security blogs/ articles.

The project includes 3 main steps:
1. Scrape data from articles by using `Beautifulsoup`
2. Extract entities from extracted paragraphs by using `Azure Text Analytics Prebuilt Model`
3. Extract the relations between pairs of two entities by using extracting triple from `Stanford Openie`
4. Build knowledge by using `Gremlin` queries and storing to `Azure Cosmos DB`

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
│   │   ├── articles_urls.txt                   <- Articles' urls
│   │   └── urls.txt                            <- Contain 4 main urls to crawl data automatically
│
├── samples/                                    <- Knowledge Graph Sample
│   └── kb.PNG                                  <- Knowledge Graph Sample
│
├── .gitignore
├── README.md                                   <- README for inference
├── execute_pipeline.py                         <- Execute main pipeline from web scrape to extract entities/ relation and insert into DB
├── knowledge_graph.py                          <- Knowledge graph queries
├── relation_extractor.py                       <- Entities and relation extraction
├── requirements.txt                            <- Package requirements
├── test.py                                     <- Testing (Implementing)
└── web_scrape.py                               <- Web scraping
```

# Getting Started

## Package requirement
>- Python 3.8.16
>- azure-ai-textanalytics==5.2.1
>- gremlinpython==3.4.13
>- spacy==3.5.1

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
`stanford_openie` is used to extract a triple (subject-verb-object) from a sentence, this is an important step to find the relation between two entities. The installation of stanford_openie would be done by using `pip install stanford_openie` version specified in `requirement.txt` but you need to ensure that Java JDK is already installed in your computer.

To check and install JDK version, please access to the link: [Download JDK](https://www.oracle.com/java/technologies/downloads/)

# Run the pipeline
In the `config.py`, you need to replace your own services key, credential to access to `Azure Text Analytics` and `Cosmos DB`.

```
# Credentials to language services
LANGUAGE_SERVICE_KEY = YOUR_LANGUAGE_SERVICE_KEY
LANGUAGE_SERVICE_ENDPOINT = YOUR_LANGUAGE_SERVICE_ENDPOINT

# CosmosDB
COSMOSDB_WWS = YOUR_COSMOSDB_WWS
COSMOSDB_USERNAME = YOUR_COSMOSDB_USERNAME
COSMOSDB_PASSWORD = YOUR_COSMOSDB_PASSWORD
```

Use the command below to run the inference
```bash
python execute_pipeline.py
```

After run the query, access to the cosmosdb, you can query data by using Gremlin or query by interact in UI. The output will look as below:
<img src="samples/kb.png" width="800" height="400">

# Model Architectures
The project contains 3 models as below:
- Model 1 - Semantic/ Name Entity Recognition (SER/NER): to classify texts into 4 classes including (OTHER, HEADER, QUESTION, ANSWER) --> final outputs of SER/NER is a list of entities (QUESTION, ANSWER). It was based on [LayoutXLM Hunggingface transformers](https://huggingface.co/docs/transformers/model_doc/layoutxlm) by Microsoft 

- Model 2 - Relation Extraction (REL): to classify the relation between every pair of question/ answer (None or KV), it is a machine learning model by using RandomForest

- Model 3 - extraNER: use pre-trained model to extract some basic classes from the entities ANSWER

Path to those models are listed in `configs.py`

