from igraph import *
#import json

import numpy as np
import copy
import random
import timeit

#import matplotlib.pyplot as plt


HighValue=111111111111
OurCapacity=100000000
our_base_fee=1
our_fee_rate=1

def_fee_rate=1
def_base_fee=1000
#txValue=1000
#txValueSet=[1,100,10000]
txValueSet=[10000]

ChCost=1024
div=2

#K=5
T=50

testFlag=0

def CostofTxCuttingEdges(graph,txAmount):
    graph.delete_edges(graph.es.select(capacity_lt=txAmount))

    for edge in graph.es:
        if edge['capacity'] >= txAmount:
            edge['txCost']=int(edge['base_fee']*1+(edge['fee_rate']*txAmount)/1000 )
        if edge['txCost']==0: # This is necessary for betweeenness calculation
            edge['txCost']=1
    
    return graph


def TopKBetweennessNodes(graph,k):
    btw= np.array(graph.betweenness(weights='txCost',directed=True))
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
    
    return index 

def UpdateEBC(fee_in,e_index):
    graph_global.es[e_index]['txCost']=fee_in
    edge_betwenness= np.array(graph_global.edge_betweenness(weights='txCost',directed=True))
    #e_index=edge_global.index
    ebc=edge_betwenness[e_index]
    graph_global.es[e_index]['edgebetweenness']=ebc
    return ebc

def MaximizeChannelReward(minFee,maxFee):
    global maxRew
    global globalmaxRew
    global maxRewFee
    global EBC_global
    global e_index
#    print '     minFee=',minFee
#    print '     maxFee=',maxFee
#    print '     maxRew=',maxRew
#    print '     maxRewFee=',maxRewFee


    ER = np.zeros(div)
    ER_max = np.zeros(div)
    
    # Base
    if maxFee-minFee <= div:
#        print '   in_base',minFee,maxFee
        for fee in np.arange(minFee,maxFee+1):
#            print 'f=',fee

            if EBC_global[fee]==0:
                ebc=UpdateEBC(fee,e_index)
                EBC_global[fee]=ebc
            else:
                ebc=EBC_global[fee]
            
            ER_local=ebc*fee
#            print '     ebc=', ebc
#            print '     ER=',ER_local
            if ER_local> globalmaxRew:
                maxRewFee=fee
                globalmaxRew =ER_local
                maxRew=globalmaxRew
        
        return
    
    else:
#        print '   in_recursion'
        # Recursive part
        for index1 in np.arange(0,div):
            fee=((maxFee-minFee)*index1/div)+minFee
#            print 'f=',fee
 
            if EBC_global[fee]==0:
                ebc=UpdateEBC(fee,e_index)
                EBC_global[fee]=ebc
            else:
                ebc=EBC_global[fee]
            
            ER[index1]=ebc*fee
#            print '     ebc=', ebc
#            print '     ER=',ER[index1]
            if ER[index1]> globalmaxRew:
                maxRewFee=fee
                globalmaxRew =ER[index1]
                maxRew=globalmaxRew
            #print 'EBC:  ', graph.es[edge.index]['edgebetweenness']
            ER_max[index1]= ebc* ( ((maxFee-minFee)*(index1+1)/div)+minFee )
#            print '     ER_max=',ER_max[index1]
            if ER[index1]==0:
#                print '   break'
                break
        
        
        for index1 in np.arange(0,div):
            
            if (ER_max[index1] > globalmaxRew):
                rec_minFee= ((maxFee-minFee)*index1/div)+minFee
                rec_maxFee= ((maxFee-minFee)*(index1+1)/div)+minFee
                MaximizeChannelReward(rec_minFee,rec_maxFee)
#            else:
#                rec_minFee= ((maxFee-minFee)*index1/div)+minFee
#                rec_maxFee= ((maxFee-minFee)*(index1+1)/div)+minFee
#                print '   discard',rec_minFee,'-',rec_maxFee
#            




txValue = txValueSet[0]
print 'txValue=',txValue

mid_graph=load('midgraphw2con_new.txt',format='pickle')

print 'Input graph'
print summary(mid_graph)

graph_deleted_edges=CostofTxCuttingEdges(mid_graph,txValue)
print 'Graph after edges deleted'
print summary(graph_deleted_edges)

NoV=len(graph_deleted_edges.vs)

txLen = len(txValueSet)

reward = np.zeros(NoV)
reward_fee = np.zeros(NoV)

globalmaxRew=0

graph_new=copy.deepcopy(graph_deleted_edges)

edge1=graph_new.es.find(_from=NoV-1,_to=2796)
edge1['txCost']=20
edge2=graph_new.es.find(_from=NoV-1,_to=1223)
edge2['txCost']=1024

CreateChannel(graph_new,NoV-1,1223,OurCapacity,1023,0,txValue)


print 'Our nodes starting connections: '
for edge in graph_new.es.select(_from=NoV-1):
    print edge.tuple

for K in np.arange(3600,NoV-1): # The last node is our node
    if graph_new.degree(K)==0:
        reward[K]=ChCost*4936 # 2x lcc = 4894. I do not know why there is difference of 42!
        reward_fee[K]=ChCost
        print 'K=',K
        print reward[K],reward_fee[K], ', Degree=0'
    else:
        graph_global=copy.deepcopy(graph_new)
    
        print 'K=',K
    
        #our_node=graph.vs.find(pub_key='our_node_pk')
        e_index=CreateChannel(graph_global,NoV-1,K,OurCapacity,our_base_fee,our_fee_rate,txValue)
        
        EBC_global= np.zeros(ChCost+1)
        maxRewFee=1
        maxRew=0
    
        MaximizeChannelReward(1,ChCost)
        reward[K] = maxRew
        reward_fee[K]= maxRewFee
    
        print reward[K],reward_fee[K]


array1= np.array(reward)
array2= np.array(reward_fee)
top20_improvement= array1.argsort()[-20:][::-1]

print 'Top 20 Nodes'
print top20_improvement

print 'Top 20 Rewards'
print array1[top20_improvement]

print 'Top 20 Reward Fees'
print array2[top20_improvement]