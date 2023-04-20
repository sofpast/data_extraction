import asyncio
import glob
import sys
import traceback

import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

import numpy as np
import pandas as pd
import requests
import spacy
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from gremlin_python.driver import client, protocol, serializer
from gremlin_python.driver.protocol import GremlinServerError
from openie import StanfordOpenIE

from knowledge_graph import *
from relation_extractor import *
from web_scrape import *

nlp = spacy.load('en_core_web_sm')

# words2check = config.words2check
# main_urls_path = config.main_urls_path

# headers to pass security check
ua = UserAgent()
headers = {'User-Agent':str(ua.chrome)}

def extract_vertice_edges(existing_urls_path, en_to_keep, special_chars):
    # Gremlin queries
    _gremlin_insert_vertices = _gremlin_insert_edges = []
    entities_df = triple_df = pd.DataFrame()

    # open urls
    existing_urls = get_existing_urls(existing_urls_path)

    for url in existing_urls:
        sent_text = scrape_web(url, nlp, headers)
        # get triple from stanford_openie
        triple_df = get_triple(sent_text)
        
        # extract entities
        # entities_df = extract_entity(sent_text)
        entities_df = pd.read_pickle('data/tmp/en3/en3.pkl')

        if triple_df.shape[0] > 0 and entities_df.shape[0] > 0:
            entities_df = entities_df[entities_df['entity_category'].isin(en_to_keep)]
            entities_df['entity'] = entities_df['entity'].apply(lambda x: remove_char(special_chars, x))
            entities_df = entities_df.sort_values('entity_score', ascending=False).drop_duplicates('entity').sort_index()
            entities_df['subject'] = entities_df['entity']
            subject_df = pd.merge(entities_df, triple_df, how='left', on =['idx', 'subject'])
            idx_lst = subject_df[~subject_df.relation.isnull()]['idx'].unique().tolist()

            # en_rel_df
            en_rel_df = pd.DataFrame()
            for idx in idx_lst:
                sub = subject_df[subject_df.idx==idx]
                en_lst = sub[sub['relation'].isnull()]['entity'].tolist()
                sub.loc[:,'en_obj'] = sub['object'].astype(str).apply(lambda x: [en for en in en_lst if en in x])
                en_rel_df = pd.concat([en_rel_df, sub])

            en_rel_df = en_rel_df[(~en_rel_df.relation.isnull())&(en_rel_df['en_obj'].str.len()!=0)][['idx','subject', 'relation', 'en_obj']] 
            en_rel_df = en_rel_df.explode('en_obj').drop_duplicates().reset_index(drop=True)

            # prepare gremlin insert vertices queries
            df = entities_df.sort_values('entity_score', ascending=False).drop_duplicates('entity').sort_index()
            df['_addV'] = "addV('" + df['entity_category'] + "').property('id','" + df['entity'] + "').property('entity_score','"+ df['entity_score'].astype(str) + "').property('pk', 'pk')"
            df['getV'] =  "g.V().has('id','" + df['entity'] + "')"
            df['addV'] = df['getV'] + ".fold().coalesce(unfold()," + df['_addV'] + ")"
            _gremlin_insert_vertices = df['addV'].tolist()

            # prepare gremlin insert edges queries
            en_rel_df['getS'] =  "g.V().has('id','" + en_rel_df['subject'] + "')"
            en_rel_df['getD'] = "g.V().has('id','" + en_rel_df['en_obj'] + "')"
            en_rel_df['getE'] = en_rel_df['getS'] + ".outE('" + en_rel_df['relation'] + "').as('e').inV()." + en_rel_df['getD'].str[6:] + ".select('e')"
            en_rel_df['_addE'] = en_rel_df['getS'] + ".addE('" + en_rel_df['relation']+ "').to(" + en_rel_df['getD'] + ")"
            en_rel_df['addE'] = en_rel_df['getE'] + ".fold().coalesce(unfold()," + en_rel_df['_addE'] + ")"
            _gremlin_insert_edges = en_rel_df['addE'].tolist()
    
    return _gremlin_insert_vertices, _gremlin_insert_edges

if __name__ == "__main__":
    _gremlin_insert_vertices, _gremlin_insert_edges = extract_vertice_edges(config.existing_urls_path, config.en_to_keep, config.special_chars)

    # open database and insert into DB
    try:
        client = client.Client(config.COSMOSDB_WWS, 'g',
                            username=config.COSMOSDB_USERNAME,
                            password=config.COSMOSDB_PASSWORD ,
                            message_serializer=serializer.GraphSONSerializersV2d0()
                            )
        
        print("Connect to Azure Cosmos DB + Gremlin on Python!")
        # Drop the entire Graph
        print("Drop graph is on the server...")
        # cleanup_graph(client)

        # Insert all vertices
        if len(_gremlin_insert_vertices) > 0:
            print(f"Number of vertices to insert into the graph: {len(_gremlin_insert_vertices)}")
            insert_vertices(client, _gremlin_insert_vertices)
        if len(_gremlin_insert_edges) > 0:
            # Create edges between vertices
            print(f"Number of edges to insert into the graph: {len(_gremlin_insert_edges)}")
            insert_edges(client, _gremlin_insert_edges)

        # Count all vertices
        # print("Count how many vertices")
        count_vertices(client)

    except GremlinServerError as e:
        print('Code: {0}, Attributes: {1}'.format(e.status_code, e.status_attributes))
        cosmos_status_code = e.status_attributes["x-ms-status-code"]
        if cosmos_status_code == 409:
            print('Conflict error!')
        elif cosmos_status_code == 412:
            print('Precondition error!')
        elif cosmos_status_code == 429:
            print('Throttling error!')
        elif cosmos_status_code == 1009:
            print('Request timeout error!')
        else:
            print("Default error handling")
            pass