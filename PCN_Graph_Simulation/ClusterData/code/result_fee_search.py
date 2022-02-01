#from scripts_only import *

from igraph import *
#import json

import numpy as np
import copy
import random
import timeit
import math

#import matplotlib.pyplot as plt

HighValue=111111111111
OurCapacity=10000000
our_base_fee=1
our_fee_rate=1

def_base_fee=1000
def_fee_rate=1
#txValue=1000
#txValueSet=[1,100,10000]
txValueSet=[100,10000,1000000]

ChCost=10000
div=10
#K=5
T=50

testFlag=2
BC_computation_flag=0
#selected_nodes=[2796,1223,235,1163,2693,4083,1352,3653,498,1988,646,2461,3235]


def UpdateEBC(fee_in):
    graph_global.es[edge_global.index]['txCost']=fee_in
    edge_betwenness= np.array(graph_global.edge_betweenness(weights='txCost',directed=True))
    e_index=edge_global.index
    ebc=edge_betwenness[e_index]
    graph_global.es[e_index]['edgebetweenness']=ebc
    return ebc

def MaximizeChannelReward(minFee,maxFee):
    global maxRew
    global maxRewFee
    global EBC_global
    
    print '     minFee=',minFee
    print '     maxFee=',maxFee
    print '     maxRew=',maxRew
    print '     maxRewFee=',maxRewFee


    ER = np.zeros(div)
    ER_max = np.zeros(div)
    
    # Base
    if maxFee-minFee <= 10:
        print '   in_base',minFee,maxFee
        for fee in np.arange(minFee,maxFee+1):
            print 'f=',fee

            if EBC_global[fee]==0:
                ebc=UpdateEBC(fee)
                EBC_global[fee]=ebc
            else:
                ebc=EBC_global[fee]
            
            ER_local=ebc*fee
            print '     ebc=', ebc
            print '     ER=',ER_local
            if ER_local> maxRew:
                maxRewFee=fee
                maxRew=ER_local
        
        return
    
    else:
        print '   in_recursion'
        # Recursive part
        for index1 in np.arange(0,div):
            fee=((maxFee-minFee)*index1/div)+minFee
            print 'f=',fee
 
            if EBC_global[fee]==0:
                ebc=UpdateEBC(fee)
                EBC_global[fee]=ebc
            else:
                ebc=EBC_global[fee]
            
            ER[index1]=ebc*fee
            print '     ebc=', ebc
            print '     ER=',ER[index1]
            if ER[index1]> maxRew:
                maxRewFee=fee
                maxRew=ER[index1]
            
            #print 'EBC:  ', graph.es[edge.index]['edgebetweenness']
            ER_max[index1]= ebc* ( ((maxFee-minFee)*(index1+1)/div)+minFee )
            print '     ER_max=',ER_max[index1]
            if ER[index1]==0:
                print '   break'
                break
        
        
        for index1 in np.arange(0,div):
            
            if (ER_max[index1] > maxRew):
                rec_minFee= ((maxFee-minFee)*index1/div)+minFee
                rec_maxFee= ((maxFee-minFee)*(index1+1)/div)+minFee
                MaximizeChannelReward(rec_minFee,rec_maxFee)
            else:
                rec_minFee= ((maxFee-minFee)*index1/div)+minFee
                rec_maxFee= ((maxFee-minFee)*(index1+1)/div)+minFee
                print '   discard',rec_minFee,'-',rec_maxFee
                #return
            


#low_graph=load('graph_with_capacity_lowtx.txt',format='pickle')
#mid_graph=load('graph_with_capacity_midtx.txt',format='pickle')
#high_graph=load('graph_with_capacity_hightx.txt',format='pickle')

print 'ChCost:',ChCost
print 'Div:', div

print '---------------- Low graph --------------------------'

graph_global=load('graph_with_capacity_lowtx.txt',format='pickle')

print summary(graph_global)

ournode_global=graph_global.vs.find(pub_key='our_node_pk')
out_edges= np.array( graph_global.es.select(_from=ournode_global.index) )
for edge in out_edges:
    
    graph_global=load('graph_with_capacity_lowtx.txt',format='pickle')
    
    print 'Edge with node:', edge.target

    EBC_global= np.zeros(ChCost+1)
    maxRewFee=1
    maxRew=0

    edge_global=edge
    MaximizeChannelReward(1,ChCost)
    
    print '-----------------'
    print 'Edge with node:', edge.target
    print 'Max Rewarding Fee:', maxRewFee
    print 'Max Reward:', maxRew
    print '-----------------'


print '---------------- Mid graph --------------------------'

graph_global=load('graph_with_capacity_midtx.txt',format='pickle')

print summary(graph_global)

ournode_global=graph_global.vs.find(pub_key='our_node_pk')
out_edges= np.array( graph_global.es.select(_from=ournode_global.index) )
for edge in out_edges:
    
    graph_global=load('graph_with_capacity_midtx.txt',format='pickle')
    
    print 'Edge with node:', edge.target

    EBC_global= np.zeros(ChCost+1)
    maxRewFee=1
    maxRew=0

    edge_global=edge
    MaximizeChannelReward(1,ChCost)
    
    print '-----------------'
    print 'Edge with node:', edge.target
    print 'Max Rewarding Fee:', maxRewFee
    print 'Max Reward:', maxRew
    print '-----------------'

print '---------------- High graph --------------------------'

graph_global=load('graph_with_capacity_hightx.txt',format='pickle')

print summary(graph_global)

ournode_global=graph_global.vs.find(pub_key='our_node_pk')
out_edges= np.array( graph_global.es.select(_from=ournode_global.index) )
for edge in out_edges:
    
    graph_global=load('graph_with_capacity_hightx.txt',format='pickle')
    
    print 'Edge with node:', edge.target

    EBC_global= np.zeros(ChCost+1)
    maxRewFee=1
    maxRew=0

    edge_global=edge
    MaximizeChannelReward(1,ChCost)
    
    print '-----------------'
    print 'Edge with node:', edge.target
    print 'Max Rewarding Fee:', maxRewFee
    print 'Max Reward:', maxRew
    print '-----------------'

