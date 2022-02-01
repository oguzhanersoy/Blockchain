from igraph import *
#import json
from scripts_only import *

import numpy as np
import copy
import random
import timeit
import multiprocessing
from multiprocessing import Pool

import matplotlib.pyplot as plt
global NumberofActive
NumberofActive=0

HighValue=111111111111
OurCapacity=100000000
our_base_fee=1
our_fee_rate=1

def_fee_rate=1
def_base_fee=1000
#txValue=1000
#txValueSet=[1,100,10000]
txValueSet=[10000]

ChCost=8192
div=2

#K=5
T=20

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
            if ER_local>= globalmaxRew:
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
            if ER[index1]>= globalmaxRew:
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


def ComputeTotalGraphReward(graph_new):
    
    edge_betwenness= np.array(graph_new.edge_betweenness(weights='txCost',directed=True))
    for index in np.arange(0,len(graph_new.es)):
            graph_new.es[index]['edgebetweenness']=edge_betwenness[index]
    
    edge_list1 = graph_new.es.select(_from=NoV-1)
    print 'Edges: '
    Totalrew=0
    for edge in edge_list1:
        print edge.tuple
        print graph_new.es[edge.index]
        Totalrew = Totalrew + edge['txCost']*edge['edgebetweenness']
    print 'Total reward:', Totalrew
    
    return Totalrew



def ThreadFunction(K):

    maxRewFee[K]=1
    maxRew[K]=0
    graph_global=copy.deepcopy(graph_new)

    e_index=CreateChannel(graph_global,NoV-1,K,OurCapacity,our_base_fee,our_fee_rate,txValue)

    global REW_global
    global edge_REW_global
    global maxRewFee
    global maxRew

    MaximizeChannelReward(1,ChCost,e_index,graph_global,K)
    maxRew[K]
    maxRewFee[K]

    print 'K=',K,maxRew[K],maxRewFee[K]


def ComputeResults(selectedNodes):
    
    array1= np.zeros(len(selectedNodes)+1)
    array2= np.zeros(len(selectedNodes)+1)
    
    globalmaxRew=ComputeTotalGraphReward(graph_new)
    
    array1[0]=globalmaxRew
    
    for K in selectedNodes:
        ThreadFunction(K)
        CreateChannel(graph_new,NoV-1,K,OurCapacity,maxRewFee[K],0,txValue)
        globalmaxRew=ComputeTotalGraphReward(graph_new)
    
    
    
    for k in np.arange(len(selectedNodes)):
        array1[k+1]=maxRew[selectedNodes[k]]
        array2[k+1]=maxRewFee[selectedNodes[k]]
    
    print 'Selected Nodes'
    print selectedNodes
    
    print 'Rewards'
    print array1
    
    print 'Reward Fees'
    print array2
    
    return array1

def SelectKRandomNodes(graph,K):
    flag=True
    while flag:
        randomNodes=random.sample(range(0,len(graph.vs)-2),K)
        flag=False
        for node in randomNodes:
            #print node, graph.degree([node])
            if graph.degree([node])==[0]:
                flag=True
    
    return randomNodes

def SelectKDifferentNodes(Nodelist,K):
    count=0
    list1=np.zeros(len(Nodelist))
    for i in Nodelist:
        if i==2796:
           continue
        if i==1163:
           continue
        list1[count]=int(i)
        count=count+1
    

    list_int=np.array(list1, dtype=np.int)

    return list_int[0:K]

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


#'''Betweenness'''
#print '----------Betweenness'
#graph_new=copy.deepcopy(graph_deleted_edges)
#edge1=graph_new.es.find(_from=NoV-1,_to=2796)
#edge1['txCost']=1010
#edge2=graph_new.es.find(_from=NoV-1,_to=1223)
#edge2['txCost']=1010
#REW_global= np.zeros((NoV,ChCost+1))
#edge_REW_global= np.zeros((NoV,ChCost+1))
#maxRewFee=np.zeros(NoV)
#maxRew=np.zeros(NoV)
#globalmaxRew=ComputeTotalGraphReward(graph_new)
#
#BNodes_in=TopKBetweennessNodes(graph_new,T+3)
#BNodes=SelectKDifferentNodes(BNodes_in,T)
#result_between=ComputeResults(BNodes)
#np.save('MidTxNew/result_between.npy',result_between)
#np.save('MidTxNew/BNodes.npy',BNodes)

#'''PageRank'''
#print '----------PageRank'
#graph_new=copy.deepcopy(graph_deleted_edges)
#edge1=graph_new.es.find(_from=NoV-1,_to=2796)
#edge1['txCost']=1010
#edge2=graph_new.es.find(_from=NoV-1,_to=1223)
#edge2['txCost']=1010
#REW_global= np.zeros((NoV,ChCost+1))
#edge_REW_global= np.zeros((NoV,ChCost+1))
#maxRewFee=np.zeros(NoV)
#maxRew=np.zeros(NoV)
#globalmaxRew=ComputeTotalGraphReward(graph_new)
#
#PRNodes_in=TopKPageRankNodes(graph_new,T+3)
#PRNodes=SelectKDifferentNodes(PRNodes_in,T)
#result_pagerank=ComputeResults(PRNodes)
#np.save('MidTxNew/result_pagerank.npy',result_pagerank)
#np.save('MidTxNew/PRNodes.npy',PRNodes)

#'''Degree'''
#print '----------Degree'
#graph_new=copy.deepcopy(graph_deleted_edges)
#edge1=graph_new.es.find(_from=NoV-1,_to=2796)
#edge1['txCost']=1010
#edge2=graph_new.es.find(_from=NoV-1,_to=1223)
#edge2['txCost']=1010
#REW_global= np.zeros((NoV,ChCost+1))
#edge_REW_global= np.zeros((NoV,ChCost+1))
#maxRewFee=np.zeros(NoV)
#maxRew=np.zeros(NoV)
#globalmaxRew=ComputeTotalGraphReward(graph_new)
#
#DNodes_in=TopKDegreeNodes(graph_new,T+3)
#DNodes=SelectKDifferentNodes(DNodes_in,T)
#result_degree=ComputeResults(DNodes)
#np.save('MidTxNew/result_degree.npy',result_degree)
#np.save('MidTxNew/DNodes.npy',DNodes)

epochNum=1
#'''Random'''
#print '----------Random'
#global graph_new
#
#RNodes_all=np.zeros([epochNum,T],dtype=np.int)
#result_random_all=np.zeros([epochNum,T+1],dtype=np.int)
#
#for epoch in np.arange(epochNum):
#    graph_new=copy.deepcopy(graph_deleted_edges)
#    edge1=graph_new.es.find(_from=NoV-1,_to=2796)
#    edge1['txCost']=1010
#    edge2=graph_new.es.find(_from=NoV-1,_to=1223)
#    edge2['txCost']=1010
#    REW_global= np.zeros((NoV,ChCost+1))
#    edge_REW_global= np.zeros((NoV,ChCost+1))
#    maxRewFee=np.zeros(NoV)
#    maxRew=np.zeros(NoV)
#    globalmaxRew=ComputeTotalGraphReward(graph_new)
#
#    RNodes_in=SelectKRandomNodes(graph_new,T+3)
#    RNodes_all[epoch]=SelectKDifferentNodes(RNodes_in,T)
#    print RNodes_all[epoch]
#    result_random_all[epoch]=ComputeResults(RNodes_all[epoch])
#
#np.save('MidTxNew/result_random_all.npy',result_random_all)
#np.save('MidTxNew/RNodes_all.npy',RNodes_all)


'''Our Greedy Nodes'''
print '----------Greedy'
graph_new=copy.deepcopy(graph_deleted_edges)
edge1=graph_new.es.find(_from=NoV-1,_to=2796)
edge1['txCost']=1010
edge2=graph_new.es.find(_from=NoV-1,_to=1223)
edge2['txCost']=1010
REW_global= np.zeros((NoV,ChCost+1))
edge_REW_global= np.zeros((NoV,ChCost+1))
maxRewFee=np.zeros(NoV)
maxRew=np.zeros(NoV)
globalmaxRew=ComputeTotalGraphReward(graph_new)

GreedyNodes=[3265,1163,2565,3349,1508]
result_selected=ComputeResults(GreedyNodes)
np.save('MidTxNew/result_selected.npy',result_selected)
np.save('MidTxNew/GreedyNodes.npy',GreedyNodes)



result_between=np.load('MidTxNew/result_between.npy')
result_degree=np.load('MidTxNew/result_degree.npy')
result_pagerank=np.load('MidTxNew/result_pagerank.npy')
result_random_all=np.load('MidTxNew/result_random_all.npy')
result_selected=np.load('MidTxNew/result_selected.npy')

result_random=np.zeros(len(result_random_all[0]))
for epoch in np.arange(epochNum):
    for ind in np.arange(len(result_random_all[0])):
        result_random[ind]=result_random[ind]+result_random_all[epoch][ind]/epochNum

t=np.arange(0,T+1)

f1 = plt.figure(1)
plt.plot(t,result_between[:], 'ro-',t,result_degree[:], 'bs-',t,result_pagerank[:], 'g^-', t,result_random[:], 'cd-', t[0:len(result_selected)],result_selected[:], 'mh-')
plt.figlegend(('Betweenness','Degree','Pagerank','Random','Selected'),loc='lower center',ncol=5)
plt.savefig('Midtx_10000_greedy_result_final.pdf')




# Greedy
#Selected Nodes
#[697, 1163, 222]
#Rewards
#[6.93621964e+08 1.14058086e+09 1.41375002e+09]
#Reward Fees
#[3996. 2999. 3998.]

# Betweenness
#Selected Nodes
#[3540 3647 2682]
#Rewards
#[6.93400026e+08 6.93491523e+08 6.93492587e+08]
#Reward Fees
#[3997. 3997. 3998.]
