import warnings

import pandas as pd
import spacy
from fake_useragent import UserAgent
from gremlin_python.driver import client, protocol, serializer
from gremlin_python.driver.protocol import GremlinServerError

from knowledge_graph import *
from relation_extractor import *
from web_scrape import *
from logger import get_logger
import argparse

warnings.simplefilter(action='ignore', category=FutureWarning)

# define logger
logger = get_logger('BAE1_data_extraction')

# load spacy
nlp = spacy.load('en_core_web_sm')

# headers to pass security check
ua = UserAgent()
headers = {'User-Agent': str(ua.chrome)}


def extract_vertice_edges(existing_urls, en_to_keep, special_chars):
    """extract list of vertices and edges from list of urls
    """
    # Gremlin queries
    _gremlin_insert_vertices = _gremlin_insert_edges = []
    entities_df = triple_df = pd.DataFrame()
    # open urls
    # existing_urls = get_existing_urls(existing_urls_path)

    for url in existing_urls:
        sent_text = scrape_web(url, nlp, headers)
        # get triple from stanford_openie
        triple_df = get_triple(sent_text)

        # extract entities
        entities_df = extract_entity(sent_text)
        # entities_df = pd.read_pickle('data/tmp/en4.pkl')
        logger.info(f"Extracting en_rel for website: {url}")
        logger.info(
            f"Extracted entities_df shape: {entities_df.shape[0]} | triple_df shape: {triple_df.shape[0]}")

        if triple_df.shape[0] > 0 and entities_df.shape[0] > 0:
            entities_df = entities_df[entities_df['entity_category'].isin(
                en_to_keep)]
            entities_df['entity'] = entities_df['entity'].apply(
                lambda x: remove_char(special_chars, x))
            subject_df = pd.merge(entities_df, triple_df,
                                  how='left', on=['idx'])
            idx_lst = subject_df[~subject_df.relation.isnull()
                                 ]['idx'].unique().tolist()
            import pdb
            pdb.set_trace()
            # en_rel_df relation to prepare gremlin queries
            en_rel_df = pd.DataFrame()
            for idx in idx_lst:
                sub = subject_df[subject_df.idx == idx].copy()
                sub.loc[:, 'sub_match'] = sub.loc[:, ('entity', 'subject')].apply(
                    lambda x: similarity_text(x.entity, x.subject), axis=1)
                sub = sub.loc[sub['sub_match'] >= config.sub_match_thresh]
                en_lst = sub['entity'].tolist()
                sub.loc[:, 'en_obj'] = sub.loc[:, 'object'].astype(
                    str).apply(lambda x: [en for en in en_lst if en in x])
                sub = sub.loc[sub['en_obj'].str.len() != 0]
                en_rel_df = pd.concat([en_rel_df, sub])
                sub = pd.DataFrame()

            en_rel_df = en_rel_df[(~en_rel_df.relation.isnull()) & (
                en_rel_df['en_obj'].str.len() != 0)][['idx', 'entity', 'relation', 'en_obj']]
            en_rel_df = en_rel_df.explode(
                'en_obj').drop_duplicates().reset_index(drop=True)
            logger.info(f"en_rel_df shape: {en_rel_df.shape[0]}")

            # prepare gremlin insert vertices queries
            df = entities_df.sort_values(
                'entity_score', ascending=False).drop_duplicates('entity').sort_index()
            df['_addV'] = "addV('" + df['entity_category'] + "').property('id','" + df['entity'] + \
                "').property('entity_score','" + \
                df['entity_score'].astype(str) + "').property('pk', 'pk')"
            df['getV'] = "g.V().has('id','" + df['entity'] + "')"
            df['addV'] = df['getV'] + \
                ".fold().coalesce(unfold()," + df['_addV'] + ")"
            _gremlin_insert_vertices = df['addV'].tolist()

            # prepare gremlin insert edges queries
            en_rel_df['getS'] = "g.V().has('id','" + en_rel_df['entity'] + "')"
            en_rel_df['getD'] = "g.V().has('id','" + en_rel_df['en_obj'] + "')"
            en_rel_df['getE'] = en_rel_df['getS'] + \
                ".outE('" + en_rel_df['relation'] + "').as('e').inV()." + \
                en_rel_df['getD'].str[6:] + ".select('e')"
            en_rel_df['_addE'] = en_rel_df['getS'] + \
                ".addE('" + en_rel_df['relation'] + \
                "').to(" + en_rel_df['getD'] + ")"
            en_rel_df['addE'] = en_rel_df['getE'] + \
                ".fold().coalesce(unfold()," + en_rel_df['_addE'] + ")"
            _gremlin_insert_edges = en_rel_df['addE'].tolist()

    return _gremlin_insert_vertices, _gremlin_insert_edges


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--drop_graph", action='store_true',
                        help="Drop existing graph before inserting")
    parser.add_argument("--mode", type=str, default="urls_from_txt",
                        help="Run mode (urls_from_txt/auto_scrape_urls)")

    args = parser.parse_args()
    new_urls = []

    if args.mode == "urls_from_txt":
        existing_urls = get_existing_urls(config.existing_urls_path)
        _gremlin_insert_vertices, _gremlin_insert_edges = extract_vertice_edges(
            existing_urls[:config.urls_limit], config.en_to_keep, config.special_chars)
    elif args.mode == "auto_scrape_urls":
        new_urls = get_new_urls(config.existing_urls_path,
                                config.main_urls_path, config.words2check)
        _gremlin_insert_vertices, _gremlin_insert_edges = extract_vertice_edges(
            new_urls[:config.urls_limit], config.en_to_keep, config.special_chars)

    # open database and insert into DB
    try:
        client = client.Client(config.COSMOSDB_WWS, 'g',
                               username=config.COSMOSDB_USERNAME,
                               password=config.COSMOSDB_PASSWORD,
                               message_serializer=serializer.GraphSONSerializersV2d0()
                               )
        logger.info("Connect to Azure Cosmos DB + Gremlin successfully")

        if args.drop_graph:
            # Drop the entire Graph
            logger.info("Drop graph is on the server...")
            cleanup_graph(client)

        # Insert all vertices
        if len(_gremlin_insert_vertices) > 0:
            if len(_gremlin_insert_vertices) > 100:
                v_gremlin_insert_chunks = [_gremlin_insert_vertices[i: i+config.chunk_size]
                                           for i in range(0, len(_gremlin_insert_vertices), config.chunk_size)]
                for v_chunk in v_gremlin_insert_chunks:
                    insert_vertices(client, v_chunk)
            insert_vertices(client, _gremlin_insert_vertices)
            logger.info(
                f"Number of vertices to insert into the graph: {len(_gremlin_insert_vertices)}")

        if len(_gremlin_insert_edges) > 0:
            if len(_gremlin_insert_edges) > 100:
                e_gremlin_insert_chunks = [_gremlin_insert_edges[i: i+config.chunk_size]
                                           for i in range(0, len(_gremlin_insert_edges), config.chunk_size)]
                for e_chunk in e_gremlin_insert_chunks:
                    insert_edges(client, e_chunk)
            insert_edges(client, _gremlin_insert_edges)
            logger.info(
                f"Number of edges to insert into the graph: {len(_gremlin_insert_edges)}")

        # Count all vertices
        count_vertices(client)

    except GremlinServerError as e:
        logger.debug('Code: {0}, Attributes: {1}'.format(
            e.status_code, e.status_attributes))
        cosmos_status_code = e.status_attributes["x-ms-status-code"]
        if cosmos_status_code == 409:
            logger.debug('Conflict error!')
        elif cosmos_status_code == 412:
            logger.debug('Precondition error!')
        elif cosmos_status_code == 429:
            logger.debug('Throttling error!')
        elif cosmos_status_code == 1009:
            logger.debug('Request timeout error!')
        else:
            pass
