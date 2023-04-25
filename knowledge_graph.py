import asyncio
import glob
import sys
import traceback

import numpy as np
import pandas as pd
from gremlin_python.driver import client, protocol, serializer
from gremlin_python.driver.protocol import GremlinServerError

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# define some basic queries
_gremlin_cleanup_graph = "g.V().drop()"

_gremlin_count_vertices = "g.V().count()"
# which threat actor targeted which organization?
# which malware has been used by the theat actor to target the organisation?
# which organization is compromised by which malware?
# which organizations did a threat actor target in the past?

_gremlin_traversals = {
    "Get all targets that attackers target to": "g.V().has('id', containing('attacker')).out('deployed on').values('id')",
    "Get the date where malware Micropsia execute": "g.V().has('id', 'Micropsia').out('execute').out('executed On').values('id')"
}


def print_status_attributes(result):
    print("\tResponse status_attributes:\n\t{0}".format(
        result.status_attributes))


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
        callback = client.submitAsync(query)
        if callback.result() is None:
            print("Something went wrong with this query: {0}".format(query))


def insert_edges(client, _gremlin_insert_edges):
    for query in _gremlin_insert_edges:
        callback = client.submitAsync(query)
        if callback.result() is None:
            print("Something went wrong with this query:\n\t{0}".format(query))


def count_vertices(client):
    callback = client.submitAsync(_gremlin_count_vertices)
    if callback.result() is not None:
        print("\tCount of vertices: {0}".format(
            callback.result().all().result()))
    else:
        print("Something went wrong with this query: {0}".format(
            _gremlin_count_vertices))


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
