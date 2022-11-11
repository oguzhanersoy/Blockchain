from igraph import *
import json

import numpy as np
import copy
import random
import timeit

import matplotlib.pyplot as plt

HighValue=111111111111
OurCapacity=10000000
our_base_fee=1
our_fee_rate=1

def_base_fee=1000
def_fee_rate=1
#txValue=1000
#txValueSet=[1,100,10000]
txValueSet=[10000]

def convert_JSON_to_graph(data):
    g=Graph(directed=True)
    i=0
    for node in data['nodes']:
        g.add_vertices(1)
        g.vs[i]['pub_key']=node['pub_key']
        i=i+1
    #print g
    j=0
    for edge in data['edges']:
        try:
            node1=g.vs.find(pub_key=edge['node1_pub'])
        except:
            print g.vs.find(pub_key=edge['node1_pub'])
            continue
        try:
            node2=g.vs.find(pub_key=edge['node2_pub'])
        except:
            print g.vs.find(pub_key=edge['node2_pub'])
            continue
        g.add_edges([(int(node1.index), int(node2.index))])
        g.es[j]['capacity']=int(edge['capacity'])
        if edge['node1_policy']!=None:
            g.es[j]['base_fee']=int(edge['node1_policy']['fee_base_msat'])
            g.es[j]['fee_rate']=int(edge['node1_policy']['fee_rate_milli_msat'])
        #else:
        #    g.es[j]['base_fee']=HighValue
        #    g.es[j]['fee_rate']=HighValue
        else:
            g.delete_edges(j)
            j=j-1

        g.add_edges([(int(node2.index), int(node1.index))])
        g.es[j+1]['capacity']=int(edge['capacity'])
        if edge['node2_policy']!=None:
            g.es[j+1]['base_fee']=int(edge['node2_policy']['fee_base_msat'])
            g.es[j+1]['fee_rate']=int(edge['node2_policy']['fee_rate_milli_msat'])
        #else:
        #    g.es[j+1]['base_fee']=HighValue
        #    g.es[j+1]['fee_rate']=HighValue
        else:
            g.delete_edges(j+1)
            j=j-1

        j=j+2


    CostofTx(g,txValue)
    return g


def CostofTx(graph,txAmount):
    for edge in graph.es:
        if edge['capacity'] >= txAmount:
            edge['txCost']=int(edge['base_fee']*1+(edge['fee_rate']*txAmount)/1000 )
        else:
            edge['txCost']=HighValue

        if edge['txCost']==0: # This is necessary for betweeenness calculation
            edge['txCost']=1

def CostofTxCuttingEdges(graph,txAmount):
    graph.delete_edges(graph.es.select(capacity_lt=txAmount))

    for edge in graph.es:
        if edge['capacity'] >= txAmount:
            edge['txCost']=int(edge['base_fee']*1+(edge['fee_rate']*txAmount)/1000 )
        if edge['txCost']==0: # This is necessary for betweeenness calculation
            edge['txCost']=1
    
    return graph

def CostofTxForEdge(graph,edge,txAmount):
    if graph.es[edge]['capacity'] >= txAmount:
        edge['txCost']=int(edge['base_fee']*1+(edge['fee_rate']*txAmount)/1000 )
    else:
        edge['txCost']=HighValue

def TopKBetweennessNodes(graph,k):
    btw= np.array(graph.betweenness(weights='txCost',directed=True))
    topk_nodes= btw.argsort()[-k:][::-1]
    return topk_nodes

def TopKDegreeNodes(graph,k):
    btw= np.array(graph.degree())
    topk_nodes= btw.argsort()[-k:][::-1]
    return topk_nodes

def TopKPageRankNodes(graph,k):
    btw= np.array(graph.pagerank())
    topk_nodes= btw.argsort()[-k:][::-1]
    return topk_nodes

def CreateChannel(graph,node,target_node,capacity,base_fee,fee_rate,txAmount):
    index=len(graph.es)
    graph.add_edges([(node,target_node)])
    graph.es[index]['capacity']=capacity
    graph.es[index]['base_fee']=int(base_fee)
    graph.es[index]['fee_rate']=int(fee_rate)
    if capacity >= txAmount:
        graph.es[index]['txCost']=int(base_fee*1+ (fee_rate*txAmount)/1000)
    else:
        graph.es[index]['txCost']=HighValue

    graph.add_edges([(target_node,node)])
    graph.es[index+1]['capacity']=capacity
    graph.es[index+1]['base_fee']=int(def_base_fee)
    graph.es[index+1]['fee_rate']=int(def_fee_rate)
    if capacity >= txAmount:
        graph.es[index+1]['txCost']=int(def_base_fee*1+ (def_fee_rate*txAmount)/1000)
    else:
        graph.es[index+1]['txCost']=HighValue

def Connect2TopKBetweennessNodes(graph,node,k,capacity,txAmount):
    topk_nodes=TopKBetweennessNodes(graph,k)
    Ch_capacity=int(capacity/k)
    for target in topk_nodes:
        CreateChannel(graph,node,target,Ch_capacity,our_base_fee,our_fee_rate,txAmount)

def Connect2SecondTopKBetweennessNodes(graph,node,k,capacity,txAmount):
    topk_nodes=TopKBetweennessNodes(graph,2*k)[k:]
    Ch_capacity=int(capacity/k)
    for target in topk_nodes:
        CreateChannel(graph,node,target,Ch_capacity,our_base_fee,our_fee_rate,txAmount)

def Connect2TopKDegreeNodes(graph,node,k,capacity,txAmount):
    topk_nodes=TopKDegreeNodes(graph,k)
    Ch_capacity=int(capacity/k)
    for target in topk_nodes:
        CreateChannel(graph,node,target,Ch_capacity,our_base_fee,our_fee_rate,txAmount)

def Connect2TopKPageRankNodes(graph,node,k,capacity,txAmount):
    topk_nodes=TopKPageRankNodes(graph,k)
    Ch_capacity=int(capacity/k)
    for target in topk_nodes:
        CreateChannel(graph,node,target,Ch_capacity,our_base_fee,our_fee_rate,txAmount)

def Connect2KRandomNodes(graph,node,k,capacity,txAmount):
    Ch_capacity=int(capacity/k)
    #print randomk_nodes[0:k]
    for target in randomk_nodes[0:k]:
        CreateChannel(graph,node,target,Ch_capacity,our_base_fee,our_fee_rate,txAmount)

def Connect2KSelectedNodes(graph,node,sel_nodes,k,capacity,base_fee,fee_rate,txAmount):
    Ch_capacity=int(capacity/k)
    #print randomk_nodes[0:k]
    for target in sel_nodes[0:k]:
        CreateChannel(graph,node,target,Ch_capacity,base_fee,fee_rate,txAmount)
