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
_gremlin_count_vertices = "g.V().count()"
# _gremlin_traversals = {
#     "Get all values that containing 2022": "g.V().hasLabel('value').has('content', containing('2022')).values()",
#     "Get all key that were extracted from xNER": "g.V().hasLabel('key').has('key_bbox', '[]')",
#     "Get all values of key extracted by xNER": "g.V().hasLabel('key').has('key_bbox', '[]').out('knows').hasLabel('value').values('content')",
#     "Get all values of key that contain 'am'": "g.V().hasLabel('key').has('content', containing('am')).out('knows').hasLabel('value').values('content') ",
#     "Get all values that key is befund": "g.V().hasLabel('key').has('content', containing('efund')).out('knows').hasLabel('value').values('content')"
# }

# g.V().hasLabel('Organization').values('id')
# Haaretz, Organization, phishing

# _gremlin_drop_operations = {
#     "Drop Edge - Thomas no longer knows Mary": "g.V('thomas').outE('knows').where(inV().has('id', 'mary')).drop()",
#     "Drop Vertex - Drop Thomas": "g.V('thomas').drop()"
# }

def print_status_attributes(result):
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


def insert_vertices(client, _gremlin_insert_vertices):
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


def insert_edges(client, _gremlin_insert_edges):

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


def update_vertices(client):
    for query in _gremlin_update_vertices:
        print("\n> {0}\n".format(query))
        callback = client.submitAsync(query)
        if callback.result() is not None:
            print("\tUpdated this vertex:\n\t{0}\n".format(
                callback.result().all().result()))
        else:
            print("Something went wrong with this query:\n\t{0}".format(query))

        print_status_attributes(callback.result())
        print("\n")

    print("\n")


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


