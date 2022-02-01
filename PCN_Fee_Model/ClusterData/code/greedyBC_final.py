from igraph import *
#import json

import numpy as np
import copy
import random
import timeit
import multiprocessing
from multiprocessing import Pool

#import matplotlib.pyplot as plt
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
txValueSet=[1000000]

ChCost=8192
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


def ThreadFunction(K):
    #print 'Start-',K
    if graph_new.degree(K)==0:
        reward[K]=0 # 2x lcc = 4894. I do not know why there is difference of 42!
        reward_fee[K]=0
        print 'K=',K, reward[K],reward_fee[K], ', Degree=0'
    else:
#        REW_global= np.zeros(ChCost+1)
#        edge_REW_global= np.zeros(ChCost+1)
        maxRewFee[K]=1
        maxRew[K]=0
        graph_global=copy.deepcopy(graph_new)
    
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
edge1['txCost']=2000
edge2=graph_new.es.find(_from=NoV-1,_to=1223)
edge2['txCost']=2000


##### Create the new channels here
CreateChannel(graph_new,NoV-1,697,OurCapacity,3996,0,txValue)
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

p = Pool(64)
p.map(ThreadFunction, np.arange(0,NoV-1))
p.close()
p.join()
# for K in np.arange(0,NoV-1):
#      # The last node is our node
#
# #        ThreadFunction(K)
#         p=multiprocessing.Process(target=ThreadFunction, args=(K,reward,reward_fee))
#         processes.append(p)
#         p.start()
#
#
# #        t = threading.Thread(target=ThreadFunction, args=(K,))
# #        threads.append(t)
# #        t.start()
#
# """"DEGISECEK"""
# for x in processes:
#     x.join()

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


for k in np.arange(len(reward)):
    array1[k]=int(reward[k])
    array2[k]=int(reward_fee[k])

top20_improvement= array1.argsort()[-20:][::-1]

print 'Top 20 Nodes'
print top20_improvement

print 'Top 20 Rewards'
print array1[top20_improvement]

print 'Top 20 Reward Fees'
print array2[top20_improvement]



#with open('workfile','a') as f:
#    f.write(str('txValue= %s \n' %txValue))
#    f.write(str('Input graph '))
#    f.write(str(summary(mid_graph) ))
#    f.write(str('\n Graph after edges deleted'))
#    f.write(str(summary(graph_deleted_edges)))
#    f.write(str('\n Our nodes starting connections: '))
#    for edge in graph_new.es.select(_from=NoV-1):
#        f.write(str(edge.tuple))
#
#f.close()


#print 'txValue=',txValue
#print 'Input graph'
#print summary(mid_graph)
#print 'Graph after edges deleted'
#print summary(graph_deleted_edges)
#
#print 'Our nodes starting connections: '
#for edge in graph_new.es.select(_from=NoV-1):
#    print edge.tuple
#
#
#for edge in edge_list1:
#    print graph_new.es[edge.index]
#    Initialrew = Initialrew + edge['txCost']*edge['edgebetweenness']
#print 'Initial reward:', Initialrew
#
#time1= timeit.default_timer()
#
#print 'Starting Time:',time1
#
#print 'Ending Time:',time2
#
#print '----Computaion Time----', time2-time1
#
#print 'Top 20 Nodes'
#print top20_improvement
#
#print 'Top 20 Rewards'
#print array1[top20_improvement]
#
#print 'Top 20 Reward Fees'
#print array2[top20_improvement]

#
#Top 20 Nodes
#[  66   71   91   12   36   16   56   27   48   88    8    5   24    0
#   32   64   20   29 1542 1538]
#Top 20 Rewards
#[5.31268380e+08 5.24447623e+08 5.07189308e+08 4.29847648e+08
# 3.80176384e+08 3.80133616e+08 3.79967392e+08 3.79813856e+08
# 3.79809472e+08 3.75390960e+08 3.65275600e+08 3.60463526e+08
# 3.60389600e+08 3.56836277e+08 3.55836543e+08 3.55503600e+08
# 3.55503526e+08 3.55429600e+08 0.00000000e+00 0.00000000e+00]
#Top 20 Reward Fees
#[2997. 2998. 2897. 8192. 8192. 8192. 8192. 8192. 8192. 8192. 4000. 4999.
# 4000. 2749. 2999. 5000. 4999. 4000.    0.    0.]




#/home/oguzhan/Desktop/PaymentChannels/Code/ClusterData/code/greedyBC_final.py:214: SyntaxWarning: name 'maxRewFee' is used prior to global declaration
#  global maxRewFee
#/home/oguzhan/Desktop/PaymentChannels/Code/ClusterData/code/greedyBC_final.py:215: SyntaxWarning: name 'maxRew' is used prior to global declaration
#  global maxRew
#txValue= 1000000
#Input graph
#IGRAPH D--- 4619 68733 -- 
#+ attr: pub_key (v), base_fee (e), capacity (e), fee_rate (e), txCost (e)
#None
#Graph after edges deleted
#IGRAPH D--- 4619 32193 -- 
#+ attr: pub_key (v), base_fee (e), capacity (e), fee_rate (e), txCost (e)
#None
#Our nodes starting connections: 
#(4618, 2796)
#(4618, 1223)
#igraph.Edge(<igraph.Graph object at 0x7f3160055240>, 32189, {'txCost': 2000, 'base_fee': 1, 'capacity': 5000000, 'fee_rate': 1, 'edgebetweenness': 82.0})
#igraph.Edge(<igraph.Graph object at 0x7f3160055240>, 32191, {'txCost': 2000, 'base_fee': 1, 'capacity': 5000000, 'fee_rate': 1, 'edgebetweenness': 177558.80000000002})
#Initial reward: 355281600.00000006
#Starting Time: 1568907411.69
#K= 4 0 0 , Degree=0
#K= 28 0 0 , Degree=0
#K= 16 380133616.00000006 8192.0
#K= 17 0 0 , Degree=0
#K= 12 429847648.0 8192.0
#K= 18 0.0 1.0
#K= 13 0.0 1.0
#K= 24 360389600.00000006 4000.0
#K= 8 365275600.00000006 4000.0
#K= 5 360463526.0 4999.0
#K= 0 356836277.00000006 2749.0
#K= 14 0.0 1.0
#K= 9 0.0 1.0
#K= 10 0 0 , Degree=0
#K= 29 355429600.0 4000.0
#K= 30 0 0 , Degree=0
#K= 31 0 0 , Degree=0
#K= 6 0.0 1.0
#K= 20 355503526.0 4999.0
#K= 19 0.0 1.0
#K= 25 0.0 1.0
#K= 36 380176384.00000006 8192.0
#K= 1 0.0 1.0
#K= 15 0.0 1.0
#K= 40 0 0 , Degree=0
#K= 41 0 0 , Degree=0
#K= 42 0 0 , Degree=0
#K= 26 0.0 1.0
#K= 11 0.0 1.0
#K= 44 0 0 , Degree=0
#K= 7 0.0 1.0
#K= 37 0.0 1.0
#K= 38 0 0 , Degree=0
#K= 45 0.0 1.0
#K= 46 0 0 , Degree=0
#K= 27 379813856.0 8192.0
#K= 48 379809472.00000006 8192.0
#K= 49 0 0 , Degree=0
#K= 52 0.0 1.0
#K= 47 0.0 1.0
#K= 56 379967392.0 8192.0
#K= 57 0 0 , Degree=0
#K= 43 0.0 1.0
#K= 2 0.0 1.0
#K= 21 0.0 1.0
#K= 22 0 0 , Degree=0
#K= 23 0 0 , Degree=0
#K= 39 0.0 1.0
#K= 68 0 0 , Degree=0
#K= 50 0.0 1.0
#K= 51 0 0 , Degree=0
#K= 72 0.0 1.0
#K= 53 0.0 1.0
#K= 58 0.0 1.0
#K= 59 0 0 , Degree=0
#K= 60 0.0 1.0
#K= 32 355836543.66666675 2999.0
#K= 73 0.0 1.0
#K= 76 0.0 1.0
#K= 77 0.0 1.0
#K= 69 0.0 1.0
#K= 78 0.0 1.0
#K= 79 0 0 , Degree=0
#K= 70 0.0 1.0
#K= 54 0.0 1.0
#K= 55 0 0 , Degree=0
#K= 61 0.0 1.0
#K= 3 0.0 1.0
#K= 88 375390960.00000006 8192.0
#K= 33 0.0 1.0
#K= 34 0 0 , Degree=0
#K= 74 0.0 1.0
#K= 80 0.0 1.0
#K= 89 0.0 1.0
#K= 81 0.0 1.0
#K= 82 0 0 , Degree=0
#K= 83 0 0 , Degree=0
#K= 92 0.0 1.0
#K= 84 0.0 1.0
#K= 62 0.0 1.0
#K= 63 0 0 , Degree=0
#K= 96 0 0 , Degree=0
#K= 71 524447623.996065 2998.0
#K= 64 355503600.00000006 5000.0
#K= 65 0 0 , Degree=0
#K= 97 0.0 1.0
#K= 75 0.0 1.0
#K= 90 0.0 1.0
#K= 35 0.0 1.0
#K= 85 0.0 1.0
#K= 86 0 0 , Degree=0
#K= 93 0.0 1.0
#K= 94 0 0 , Degree=0
#K= 95 0 0 , Degree=0
#K= 87 0.0 1.0
#K= 98 0.0 1.0
#K= 66 531268380.0 2997.0
#K= 67 0 0 , Degree=0
#K= 91 507189308.0000003 2897.0
#K= 99 0.0 1.0
#Ending Time: 1568908809.83
#----Computaion Time---- 1398.13707995
#Top 20 Nodes
#[  66   71   91   12   36   16   56   27   48   88    8    5   24    0
#   32   64   20   29 1542 1538]
#Top 20 Rewards
#[5.31268380e+08 5.24447623e+08 5.07189308e+08 4.29847648e+08
# 3.80176384e+08 3.80133616e+08 3.79967392e+08 3.79813856e+08
# 3.79809472e+08 3.75390960e+08 3.65275600e+08 3.60463526e+08
# 3.60389600e+08 3.56836277e+08 3.55836543e+08 3.55503600e+08
# 3.55503526e+08 3.55429600e+08 0.00000000e+00 0.00000000e+00]
#Top 20 Reward Fees
#[2997. 2998. 2897. 8192. 8192. 8192. 8192. 8192. 8192. 8192. 4000. 4999.
# 4000. 2749. 2999. 5000. 4999. 4000.    0.    0.]