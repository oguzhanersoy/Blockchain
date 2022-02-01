from igraph import *
#import json

import numpy as np
import copy
import random
import timeit
import multiprocessing 

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


def ComputeTotalRew(fee_in,e_index,graph_global):
    graph_global.es[e_index]['txCost']=fee_in
    edge_betwenness= np.array(graph_global.edge_betweenness(weights='txCost',directed=True))
    for index in np.arange(0,len(graph_global.es)):
        graph_global.es[index]['edgebetweenness']=edge_betwenness[index]
    edge_list = graph_global.es.select(_from=NoV-1)
    Totalrew=0
    for edge in edge_list:
        Totalrew = Totalrew + edge['txCost']*edge['edgebetweenness']
    our_edge = graph_global.es[e_index]
    edge_rew = our_edge['txCost']*our_edge['edgebetweenness']
    rest_rew = Totalrew - edge_rew
    return edge_rew, rest_rew

def MaximizeChannelReward(minFee,maxFee,e_index,graph_global,K):
    global maxRew
    global globalmaxRew
    global maxRewFee
    global REW_global
    global edge_REW_global
#    global e_index
#    print '     minFee=',minFee
#    print '     maxFee=',maxFee
#    print '     maxRew=',maxRew
#    print '     maxRewFee=',maxRewFee


    ER = np.zeros(div+1)
    ER_max = np.zeros(div)
    
    # Base
    if maxFee-minFee <= div:
#        print '   in_base',minFee,maxFee
        for fee in np.arange(minFee,maxFee+1):
#            print 'f=',fee

            if REW_global[K][fee]==0:
                e_rew,r_rew=ComputeTotalRew(fee,e_index,graph_global)
                REW_global[K][fee]=e_rew+r_rew

                edge_REW_global[K][fee]=e_rew
#                print e_rew
#                print 'Others:',r_rew
#                print 'Total:',REW_global[fee]
#            else:
#                rew=REW_global[fee]
            
            ER_local=REW_global[K][fee]
#            print '     ebc=', ebc
#            print '     eRew=', edge_REW_global[K][fee]
#            print '     ER=',ER_local
            if ER_local> globalmaxRew:
                maxRewFee[K]=fee
                globalmaxRew =ER_local
                maxRew[K]=globalmaxRew
        
        return
    
    else:
#        print '   in_recursion'
        # Recursive part
        for index1 in np.arange(0,div+1):
            fee=((maxFee-minFee)*index1/div)+minFee
#            print 'f=',fee
 
            if REW_global[K][fee]==0:
                e_rew,r_rew=ComputeTotalRew(fee,e_index,graph_global)
                REW_global[K][fee]=e_rew+r_rew

                edge_REW_global[K][fee]=e_rew
#                print e_rew
#                print 'Others:',r_rew
#                print 'Total:',REW_global[fee]
#            else:
#                rew=REW_global[fee]
            
            ER[index1]=REW_global[K][fee]
#            print '     eRew=', edge_REW_global[K][fee]
#            print '     ER=',ER[index1]
            if ER[index1]> globalmaxRew:
                maxRewFee[K]=fee
                globalmaxRew =ER[index1]
                maxRew[K]=globalmaxRew
            #print 'EBC:  ', graph.es[edge.index]['edgebetweenness']
#            ER_max[index1]= ebc* ( ((maxFee-minFee)*(index1+1)/div)+minFee )
#            print '     ER_max=',ER_max[index1]
            if ER[index1]==0:
#                print '   break'
                break
        
        
        for index1 in np.arange(0,div):
            fee=((maxFee-minFee)*index1/div)+minFee
            fee_next=((maxFee-minFee)*(index1+1)/div)+minFee
#            print 'f=',fee
            #print 'EBC:  ', graph.es[edge.index]['edgebetweenness']
            ER_max[index1]= (ER[index1+1]-edge_REW_global[K][fee_next]) + (edge_REW_global[K][fee]*fee_next)/fee
#            print '     ER_max=',ER_max[index1]

        
        for index1 in np.arange(0,div):
            
            if (ER_max[index1] > globalmaxRew):
                rec_minFee= ((maxFee-minFee)*index1/div)+minFee
                rec_maxFee= ((maxFee-minFee)*(index1+1)/div)+minFee
                MaximizeChannelReward(rec_minFee,rec_maxFee,e_index,graph_global,K)
#            else:
#                rec_minFee= ((maxFee-minFee)*index1/div)+minFee
#                rec_maxFee= ((maxFee-minFee)*(index1+1)/div)+minFee
#                print '   discard',rec_minFee,'-',rec_maxFee
#            


def ThreadFunction(K,reward,reward_fee):
    graph_global=copy.deepcopy(graph_new)
    
    print 'Starting ',K

    #our_node=graph.vs.find(pub_key='our_node_pk')
    e_index=CreateChannel(graph_global,NoV-1,K,OurCapacity,our_base_fee,our_fee_rate,txValue)
    
    global REW_global
    global edge_REW_global
    global maxRewFee
    global maxRew

#    t = threading.Thread(target=worker, args=(i,))
#    threads.append(t)
#    t.start()

    MaximizeChannelReward(1,ChCost,e_index,graph_global,K)
    reward[K] = maxRew[K]
    reward_fee[K]= maxRewFee[K]

    print 'K=',K,reward[K],reward_fee[K]



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

graph_new=copy.deepcopy(graph_deleted_edges)

edge1=graph_new.es.find(_from=NoV-1,_to=2796)
edge1['txCost']=20
edge2=graph_new.es.find(_from=NoV-1,_to=1223)
edge2['txCost']=1024


##### Create the new channels here

####




print 'Our nodes starting connections: '
for edge in graph_new.es.select(_from=NoV-1):
    print edge.tuple

edge_betwenness= np.array(graph_new.edge_betweenness(weights='txCost',directed=True))
for index in np.arange(0,len(graph_new.es)):
        graph_new.es[index]['edgebetweenness']=edge_betwenness[index]


edge_list1 = graph_new.es.select(_from=NoV-1)
Initialrew=0
for edge in edge_list1:
    print graph_new.es[edge.index]
    Initialrew = Initialrew + edge['txCost']*edge['edgebetweenness']
print 'Initial reward:', Initialrew

time1= timeit.default_timer()

print 'Starting Time:',time1

globalmaxRew=Initialrew

processes=[]

REW_global= np.zeros((NoV,ChCost+1))
edge_REW_global= np.zeros((NoV,ChCost+1))
maxRewFee=np.zeros(NoV)
maxRew=np.zeros(NoV)

manager = multiprocessing.Manager()
reward = manager.dict()
reward_fee = manager.dict()

for K in np.arange(10,20): # The last node is our node
    if graph_new.degree(K)==0:
        reward[K]=0 # 2x lcc = 4894. I do not know why there is difference of 42!
        reward_fee[K]=0
        print 'K=',K, reward[K],reward_fee[K], ', Degree=0'
    else:
#        REW_global= np.zeros(ChCost+1)
#        edge_REW_global= np.zeros(ChCost+1)
        maxRewFee[K]=1
        maxRew[K]=0
#        ThreadFunction(K)
        p=multiprocessing.Process(target=ThreadFunction, args=(K,reward,reward_fee))
        processes.append(p)
        p.start()
#        t = threading.Thread(target=ThreadFunction, args=(K,))
#        threads.append(t)
#        t.start()

""""DEGISECEK"""
for x in processes:
    x.join()

#Thread
#K= 22 651434372.0000001 1024.0
#K= 31 651553924.0000001 768.0
#w/o Thread
#K= 22 651532962.0000001 1009.0
#K= 31 651779561.0000001 1009.0

time2= timeit.default_timer()

print 'Ending Time:',time2

print '----Computaion Time----', time2-time1

array1= np.zeros(NoV)
array2= np.zeros(NoV)

for k in reward:
    if reward[k]:
        array1[k]=int(reward[k])
        array2[k]=int(reward_fee[k])

top20_improvement= array1.argsort()[-20:][::-1]

print 'Top 20 Nodes'
print top20_improvement

print 'Top 20 Rewards'
print array1[top20_improvement]

print 'Top 20 Reward Fees'
print array2[top20_improvement]