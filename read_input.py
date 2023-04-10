import pandas as pd

from gremlin_python.driver import client, serializer, protocol
from gremlin_python.driver.protocol import GremlinServerError
import sys
import traceback
import asyncio
import glob
import numpy as np


if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

_gremlin_cleanup_graph = "g.V().drop()"

# _gremlin_insert_vertices = [
#     "g.addV('person').property('id', 'thomas').property('firstName', 'Thomas').property('age', 44).property('pk', 'pk')",
#     "g.addV('person').property('id', 'mary').property('firstName', 'Mary').property('lastName', 'Andersen').property('age', 39).property('pk', 'pk')",
#     "g.addV('person').property('id', 'ben').property('firstName', 'Ben').property('lastName', 'Miller').property('pk', 'pk')",
#     "g.addV('person').property('id', 'robin').property('firstName', 'Robin').property('lastName', 'Wakefield').property('pk', 'pk')"
# ]
# _gremlin_insert_edges = [
#     "g.V('thomas').addE('knows').to(g.V('mary'))",
#     "g.V('thomas').addE('knows').to(g.V('ben'))",
#     "g.V('ben').addE('knows').to(g.V('robin'))"
# ]

# _gremlin_update_vertices = [
#     "g.V('thomas').property('age', 45)"
# ]

_gremlin_count_vertices = "g.V().count()"

# _gremlin_traversals = {
#     "Get all persons older than 40": "g.V().hasLabel('person').has('age', gt(40)).values('firstName', 'age')",
#     "Get all persons and their first name": "g.V().hasLabel('person').values('firstName')",
#     "Get all persons sorted by first name": "g.V().hasLabel('person').order().by('firstName', incr).values('firstName')",
#     "Get all persons that Thomas knows": "g.V('thomas').out('knows').hasLabel('person').values('firstName')",
#     "People known by those who Thomas knows": "g.V('thomas').out('knows').hasLabel('person').out('knows').hasLabel('person').values('firstName')",
#     "Get the path from Thomas to Robin": "g.V('thomas').repeat(out()).until(has('id', 'robin')).path().by('firstName')"
# }


_gremlin_traversals = {
    "Get all values that containing 2022": "g.V().hasLabel('value').has('content', containing('2022')).values()",
    "Get all key that were extracted from xNER": "g.V().hasLabel('key').has('key_bbox', '[]')",
    "Get all values of key extracted by xNER": "g.V().hasLabel('key').has('key_bbox', '[]').out('knows').hasLabel('value').values('content')",
    "Get all values of key that contain 'am'": "g.V().hasLabel('key').has('content', containing('am')).out('knows').hasLabel('value').values('content') ",
    "Get all values that key is befund": "g.V().hasLabel('key').has('content', containing('efund')).out('knows').hasLabel('value').values('content')"
}

_gremlin_drop_operations = {
    "Drop Edge - Thomas no longer knows Mary": "g.V('thomas').outE('knows').where(inV().has('id', 'mary')).drop()",
    "Drop Vertex - Drop Thomas": "g.V('thomas').drop()"
}

def print_status_attributes(result):
    # This logs the status attributes returned for successful requests.
    # See list of available response status attributes (headers) that Gremlin API can return:
    #     https://docs.microsoft.com/en-us/azure/cosmos-db/gremlin-headers#headers
    #
    # These responses includes total request units charged and total server latency time.
    # 
    # IMPORTANT: Make sure to consume ALL results returend by cliient tothe final status attributes
    # for a request. Gremlin result are stream as a sequence of partial response messages
    # where the last response contents the complete status attributes set.
    #
    # This can be 
    print("\tResponse status_attributes:\n\t{0}".format(result.status_attributes))

def cleanup_graph(client):
    print("\n> {0}".format(
        _gremlin_cleanup_graph))
    callback = client.submitAsync(_gremlin_cleanup_graph)
    if callback.result() is not None:
        callback.result().all().result() 
    print("\n")
    print_status_attributes(callback.result())
    print("\n")


def insert_vertices(client):
    for query in _gremlin_insert_vertices:
        print("\n> {0}\n".format(query))
        callback = client.submitAsync(query)
        if callback.result() is not None:
            print("\tInserted this vertex:\n\t{0}".format(
                callback.result().all().result()))
        else:
            print("Something went wrong with this query: {0}".format(query))
        print("\n")
        print_status_attributes(callback.result())
        print("\n")

    print("\n")


def insert_edges(client):

    for query in _gremlin_insert_edges:
        print("\n> {0}\n".format(query))
        callback = client.submitAsync(query)
        if callback.result() is not None:
            print("\tInserted this edge:\n\t{0}\n".format(
                callback.result().all().result()))
        else:
            print("Something went wrong with this query:\n\t{0}".format(query))
        print_status_attributes(callback.result())
        print("\n")

    print("\n")


# def update_vertices(client):
#     for query in _gremlin_update_vertices:
#         print("\n> {0}\n".format(query))
#         callback = client.submitAsync(query)
#         if callback.result() is not None:
#             print("\tUpdated this vertex:\n\t{0}\n".format(
#                 callback.result().all().result()))
#         else:
#             print("Something went wrong with this query:\n\t{0}".format(query))

#         print_status_attributes(callback.result())
#         print("\n")

#     print("\n")


def count_vertices(client):
    print("\n> {0}".format(
        _gremlin_count_vertices))
    callback = client.submitAsync(_gremlin_count_vertices)
    if callback.result() is not None:
        print("\tCount of vertices: {0}".format(callback.result().all().result()))
    else:
        print("Something went wrong with this query: {0}".format(
            _gremlin_count_vertices))

    print("\n")
    print_status_attributes(callback.result())
    print("\n")


def execute_traversals(client):
    for key in _gremlin_traversals:
        print("{0}:".format(key))
        print("> {0}\n".format(
            _gremlin_traversals[key]))
        callback = client.submitAsync(_gremlin_traversals[key])
        for result in callback.result():
            print("\t{0}".format(str(result)))
        
        print("\n")
        print_status_attributes(callback.result())
        print("\n")


def execute_drop_operations(client):
    for key in _gremlin_drop_operations:
        print("{0}:".format(key))
        print("\n> {0}".format(
            _gremlin_drop_operations[key]))
        callback = client.submitAsync(_gremlin_drop_operations[key])
        for result in callback.result():
            print(result)
        print_status_attributes(callback.result())
        print("\n")


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
    df = []
    # Read json files
    # for file in glob.glob('data/*.json'):
    #     try:
    #         df = pd.read_json(file)
    #         df_kv = df['fields'].apply(pd.Series)
    #         df = pd.concat([df, df_kv], axis=1)

    #         df['k_addV'] = "g.addV('key').property('content','" + df['key'] + "').property('doc_id','"+ df['document_id'] + "').property('key_bbox', '" + df['key_bbox'].astype(str) + "').property('pk', 'pk')"
    #         df['v_addV'] = "g.addV('value').property('content','" + df['value'] + "').property('doc_id','"+ df['document_id'] + "').property('key_bbox', '" + df['value_bbox'].astype(str) + "').property('pk', 'pk')"
    #         df['addE'] = "g.V().hasLabel('key').has('content', '" + df['key'] + "').addE('knows').to(g.V().hasLabel('value').has('content', '" + df['value'] + "'))"

    #         _gremlin_insert_vertices = df['k_addV'].tolist() + df['v_addV'].tolist()

    #         _gremlin_insert_edges = df['addE'].tolist()
    #     except GremlinServerError as e:
    #         print(e)
    #         pass

    #     # Insert all vertices
    #     input("Let's insert some vertices into the graph. Press any key to continue...")
    #     insert_vertices(client)

    #     # Create edges between vertices
    #     input("Now, let's add some edges between the vertices. Press any key to continue...")
    #     insert_edges(client)

    en_df = pd.read_pickle('data/entities_df.pkl')
    rel_df = pd.read_pickle('data/relations_df.pkl')
    rel_df = rel_df.rename(columns={'idx':'has_rel'})

    merged_df = en_df.merge(rel_df, on='has_rel', how='left')
    df = merged_df.drop_duplicates(subset=['entity'], keep='first')
    df['des_uuid'] = np.NaN

    df['addV'] = "g.addV('" + df['entity_category'] + "').property('id','" + df['entity'] + "').property('entity_score','"+ df['entity_score'].astype(str) + "').property('sent_idx','"+ df.idx.astype(str) + "').property('en_idx','" + df.index.astype(str) + "').property('pk', 'pk')"
    # df['v_addV'] = "g.addV('value').property('content','" + df['value'] + "').property('doc_id','"+ df['document_id'] + "').property('key_bbox', '" + df['value_bbox'].astype(str) + "').property('pk', 'pk')"
    # df['addE'] = "g.V().hasLabel('key').has('content', '" + df['key'] + "').addE('knows').to(g.V().hasLabel('value').has('content', '" + df['value'] + "'))"

    # "g.V().hasLabel('" + sub['entity_category'] + "').has('id', '" + df['entity'] + "')"

    merged_df['getV'] = "g.V().hasLabel('" + merged_df['entity_category'] + "').has('id','" + merged_df['entity'] + "')"
    

    _gremlin_insert_vertices = df['addV'].tolist()
    _gremlin_insert_edges = []




    import pdb
    pdb.set_trace()
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
                # import pdb
                # pdb.set_trace()
                print(addE_cmd)
                _gremlin_insert_edges.append(addE_cmd)
                
        else:
            continue

    # Create edges between vertices
    # input("Now, let's add some edges between the vertices. Press any key to continue...")
    # insert_edges(client)

    # import pdb
    # pdb.set_trace()

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

    # GremlinServerError.status_code returns the Gremlin protocol status code
    # These are broad status codes which can cover various scenaios, so for more specific
    # error handling we recommend using GremlinServerError.status_attributes['x-ms-status-code']
    # 
    # Below shows how to capture the Cosmos DB specific status code and perform specific error handling.
    # See detailed set status codes than can be returned here: https://docs.microsoft.com/en-us/azure/cosmos-db/gremlin-headers#status-codes
    #
    # See also list of available response status attributes that Gremlin API can return:
    #     https://docs.microsoft.com/en-us/azure/cosmos-db/gremlin-headers#headers
    cosmos_status_code = e.status_attributes["x-ms-status-code"]
    if cosmos_status_code == 409:
        print('Conflict error!')
    elif cosmos_status_code == 412:
        print('Precondition error!')
    elif cosmos_status_code == 429:
        print('Throttling error!');
    elif cosmos_status_code == 1009:
        print('Request timeout error!')
    else:
        print("Default error handling")
        pass


input("Okay. Let's count how many vertices we have. Press any key to continue...")
count_vertices(client)

# Execute traversals and get results
input("Cool! Let's run some traversals on our graph. Press any key to continue...")
execute_traversals(client)

print("\nAnd that's all! Sample complete")
input("Press Enter to continue...")