import pandas as pd

from gremlin_python.driver import client, serializer, protocol
from gremlin_python.driver.protocol import GremlinServerError
import sys
import traceback
import asyncio
import glob
import numpy as np

from knowledge_graph import *
from relation_extractor import *

try:
    client = client.Client('wss://cosmosdbhack.gremlin.cosmos.azure.com:443/', 'g',
                           username="/dbs/threatactor-database/colls/threatactor-graph",
                           password="SHwb6lPjs2CzVvyFxp8bpALcY3oQQ2d7l9s9ydRCwtWJ7ywg5zP0Ka3Gl2LgGm4yYuR11JxNxYg9ACDbQfOMeg==",
                           message_serializer=serializer.GraphSONSerializersV2d0()
                           )

    print("Welcome to Azure Cosmos DB + Gremlin on Python!")

    # Drop the entire Graph
    input("We're about to drop whatever graph is on the server. Press any key to continue...")
    # cleanup_graph(client)

    en_to_keep = ['DateTime', 'Event', 'PersonType', 'Organization', 'Location', 'Product', 'Person']
    remove_list = ["*", "/", "&"]
    
    merged_df = pd.read_pickle('data/merged_df.pkl')
    merged_df = merged_df[merged_df['entity_category'].isin(en_to_keep)]
    merged_df['entity_bk'] = merged_df['entity']
    merged_df['entity'] = merged_df['entity'].apply(lambda x: remove_char(remove_list, x))
    # merged_df['entity'] = merged_df['entity'].str.replace("/", "")

    
    df = []
    df = merged_df.drop_duplicates(subset=['entity'], keep='first')

    df['addV'] = "g.addV('" + df['entity_category'] + "').property('id','" + df['entity'] + "').property('entity_score','"+ df['entity_score'].astype(str) + "').property('sent_idx','"+ df.idx.astype(str) + "').property('en_idx','" + df.index.astype(str) + "').property('pk', 'pk')"
 
    # merged_df['getV'] = "g.V().hasLabel('" + merged_df['entity_category'] + "').has('id','" + merged_df['entity'] + "')"
    merged_df['getV'] = "g.V().has('id','" + merged_df['entity'] + "')"

    _gremlin_insert_vertices = df['addV'].tolist()
    _gremlin_insert_edges = []

    # Insert all vertices
    input("Let's insert some vertices into the graph. Press any key to continue...")
    # insert_vertices(client)

    for idx, row in merged_df.iterrows():
        
        sub = merged_df[(merged_df.idx==idx) & (~merged_df['offset'].isnull())]
        if sub[sub['is_source']=="Y"].shape[0] > 0:
            getV_list = sub['getV'].tolist()
            relation = sub['relation'].iloc[0] 

            for i in range(1, len(getV_list)): 
                addE_cmd = ""
                addE_cmd = getV_list[0] + ".addE('" + relation + "').to(" + getV_list[i] + ")"
                print(addE_cmd)
                _gremlin_insert_edges.append(addE_cmd)
                
        else:
            continue

    # Create edges between vertices
    input("Now, let's add some edges between the vertices. Press any key to continue...")
    # insert_edges(client)

    # Update a vertex
    # input("Ah, sorry. I made a mistake. Let's change the age of this vertex. Press any key to continue...")
    # update_vertices(client)

    # Count all vertices
    input("Okay. Let's count how many vertices we have. Press any key to continue...")
    count_vertices(client)

    # Execute traversals and get results
    # input("Cool! Let's run some traversals on our graph. Press any key to continue...")
    # execute_traversals(client)

    # Drop a few vertices and edges
    # input("So, life happens and now we will make some changes to the graph. Press any key to continue...")
    # execute_drop_operations(client)

    # Count all vertices again
    # input("How many vertices do we have left? Press any key to continue...")
    # count_vertices(client)

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


input("Okay. Let's count how many vertices we have. Press any key to continue...")
# count_vertices(client)

# Execute traversals and get results
input("Cool! Let's run some traversals on our graph. Press any key to continue...")
# execute_traversals(client)

print("\nAnd that's all! Sample complete")
input("Press Enter to continue...")