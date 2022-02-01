from igraph import *
#import json

import numpy as np
import copy
import random
import timeit

#import matplotlib.pyplot as plt


HighValue=111111111111
OurCapacity=10000000
our_base_fee=1
our_fee_rate=1
#txValue=1000
#txValueSet=[1,100,10000]
txValueSet=[100]

#K=5
T=50

testFlag=0

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
    graph.es[index+1]['base_fee']=int(base_fee)
    graph.es[index+1]['fee_rate']=int(fee_rate)
    if capacity >= txAmount:
        graph.es[index+1]['txCost']=int(base_fee*1+ (fee_rate*txAmount)/1000)
    else:
        graph.es[index+1]['txCost']=HighValue

def Connect2TopKBetweennessNodes(graph,node,k,capacity,txAmount):
    topk_nodes=TopKBetweennessNodes(graph,k)
    Ch_capacity=int(capacity/k)
    for target in topk_nodes:
        CreateChannel(graph,node,target,Ch_capacity,our_base_fee,our_fee_rate,txAmount)

# def Connect2RandomKNodes(graph,node,k,capacity):
#     random_nodes=random.sample(range(0,len(graph.vs)-2),k)
#     Ch_capacity=int(capacity/k)
#     for target in random_nodes:
#         CreateChannel(graph,node,target,Ch_capacity,our_base_fee,our_fee_rate,txValue)


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

def Connect2KSelectedNodes(graph,node,k,capacity,txAmount):
    Ch_capacity=int(capacity/k)
    #print randomk_nodes[0:k]
    for target in selected_nodes[0:k]:
        CreateChannel(graph,node,target,Ch_capacity,our_base_fee,our_fee_rate,txAmount)


#def Connect2KRandomNodes2(graph,node,k,capacity,txAmount):
#    print randomk_nodes
#    Ch_capacity=int(capacity/k)
#    for target in randomk_nodes[0:k]:
#        CreateChannel(graph,node,target,Ch_capacity,our_base_fee,our_fee_rate,txAmount)

#time1= timeit.default_timer()

''' Reading the json file '''
#f = open('networkgraphv2','r')
#data= json.load(f)
#graph= convert_JSON_to_graph(data)
#Graph.save(graph,'lngraphv2.txt',format='pickle')

#loaded_graph=load('lngraphv2.txt',format='pickle')
#print summary(loaded_graph)

#selected_nodes=[2796,1223]

#loaded_graph.add_vertices(1)
#index=len(loaded_graph.vs)
#loaded_graph.vs[index-1]['pub_key']='our_node_pk'
#our_node=loaded_graph.vs.find(pub_key='our_node_pk')
#Connect2KSelectedNodes(loaded_graph,our_node,2,OurCapacity,txValue)
#
#low_graph=copy.deepcopy(loaded_graph)
#CostofTx(low_graph,1)
#Graph.save(low_graph,'lowgraphw2con.txt',format='pickle')
#mid_graph=copy.deepcopy(loaded_graph)
#CostofTx(mid_graph,100)
#Graph.save(mid_graph,'midgraphw2con.txt',format='pickle')
#high_graph=copy.deepcopy(loaded_graph)
#CostofTx(high_graph,10000)
#Graph.save(high_graph,'highgraphw2con.txt',format='pickle')


mid_graph=load('midgraphw2con.txt',format='pickle')

NoV=len(mid_graph.vs)

txLen = len(txValueSet)

BC_improvement = np.zeros(NoV)

#for txValueIndex in np.arange(0,txLen):

txValue = txValueSet[0]
print 'txValue=',txValue

graph_new=copy.deepcopy(mid_graph)
CreateChannel(graph_new,NoV-1,235,OurCapacity,our_base_fee,our_fee_rate,txValue)
CreateChannel(graph_new,NoV-1,1163,OurCapacity,our_base_fee,our_fee_rate,txValue)
CreateChannel(graph_new,NoV-1,2693,OurCapacity,our_base_fee,our_fee_rate,txValue)
CreateChannel(graph_new,NoV-1,4083,OurCapacity,our_base_fee,our_fee_rate,txValue)
CreateChannel(graph_new,NoV-1,1352,OurCapacity,our_base_fee,our_fee_rate,txValue)
CreateChannel(graph_new,NoV-1,3653,OurCapacity,our_base_fee,our_fee_rate,txValue)
CreateChannel(graph_new,NoV-1,498,OurCapacity,our_base_fee,our_fee_rate,txValue)

print 'Our nodes starting connections: '
for edge in graph_new.es.select(_from=NoV-1):
    print edge.tuple

CurrentBC = graph_new.betweenness(weights='txCost',directed=True)[NoV-1]

for K in np.arange(0,NoV-1): # The last node is our node
    graph=copy.deepcopy(graph_new)

    print 'K=',K
    
    #our_node=graph.vs.find(pub_key='our_node_pk')
    CreateChannel(graph,NoV-1,K,OurCapacity,our_base_fee,our_fee_rate,txValue)

    if testFlag==1:
        #print 'After our node is added'
        print summary(graph)

    if testFlag==1:
        print graph.betweenness(weights='txCost',directed=True)

    if testFlag==1:
        print 'Top 2K nodes having highest betweenness values'
        top2k_bnodes= TopKBetweennessNodes(graph,2*K)
        print top2k_bnodes
        print np.array(graph.betweenness(weights='txCost',directed=True))[top2k_bnodes.astype(int)]

    BC_improvement[K] = graph.betweenness(weights='txCost',directed=True)[NoV-1] - CurrentBC

    if testFlag==-1:
        print '-------'
        print BC_improvement[K]
        print '-------'
    
    print BC_improvement[K]

    if testFlag==-1:
        print 'Ournodes connections: '
        for edge in graph.es.select(_from=NoV-1):
            print edge.tuple


print 'Betweenness Centrality Improvement'
print BC_improvement

array1= np.array(BC_improvement)
top20_improvement= array1.argsort()[-20:][::-1]

print 'Top 20 BC Improvement'
print top20_improvement

