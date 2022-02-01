from scripts_only import *

from igraph import *
#import json

import numpy as np
import copy
import random
import timeit
import math

import matplotlib.pyplot as plt

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

maxRewFee=1
maxRew=0

graph_global=load('graph_with_capacity_lowtx.txt',format='pickle')
ournode_global=graph_global.vs.find(pub_key='our_node_pk')
out_edges= np.array( graph_global.es.select(_from=ournode_global.index) )
edge_global=out_edges[3]

EBC_global= np.zeros(ChCost+1)

def DistributeCapacityOverChannels(g,ournode,totalCapacity):
    edge_betwenness= np.array(g.edge_betweenness(weights='txCost',directed=True))
    for i in np.arange(0,len(edge_betwenness)):
        g.es[i]['edgebetweenness']=edge_betwenness[i]
    in_edges= np.array( g.es.select(_to=ournode.index) )
    out_edges=np.array( g.es.select(_from=ournode.index) )
    all_edges= np.concatenate( (in_edges,out_edges),axis=None )
    TotalEB=0
    for edge in all_edges:
        TotalEB= TotalEB+ g.es[edge.index]['edgebetweenness']
    for edge in all_edges:
        g.es[edge.index]['capacity'] = math.floor((g.es[edge.index]['edgebetweenness']*totalCapacity)/TotalEB)

    return g


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
            #graph_global.es[edge_global.index]['txCost']=fee
            #CostofTxCuttingEdges(graph,txAmount)
            #print 'Before: ', graph.es[edge.index]['edgebetweenness'],graph.es[edge.index]['txCost']
            if EBC_global[fee]==0:
                ebc=UpdateEBC(fee)
                EBC_global[fee]=ebc
            else:
                ebc=EBC_global[fee]
            
            ER_local=ebc*fee
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
            #graph_global.es[edge_global.index]['txCost']=fee
            #CostofTxCuttingEdges(graph,txAmount)
            #print 'Before: ', graph.es[edge.index]['edgebetweenness'],graph.es[edge.index]['txCost']
            
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
            
    



def ComputeChannelReward(g,edge_index,ebc,txCost):
    reward = ebc * txCost
    return reward

#def CalculateTotalReward(g, ournode, connectedNodes):


def DisplayBetweennessResults():
    
    result_between = np.load('SavedGraphData/between50.npy')
    result_degree = np.load('SavedGraphData/degree50.npy')
    result_pagerank = np.load('SavedGraphData/pagerank50.npy')
    result_random = np.load('SavedGraphData/random50.npy')
    result_selected = np.load('SavedGraphData/selected50.npy')
    print result_selected[0][0:10]
    #Normalizing factor= (N-1)(N-2) for directed graph of N nodes
    NF=4618*4617
    result_between=np.true_divide(result_between,NF)
    result_degree=np.true_divide(result_degree,NF)
    result_pagerank=np.true_divide(result_pagerank,NF)
    result_random=np.true_divide(result_random,NF)
    result_selected=np.true_divide(result_selected,NF)
    print result_selected[0][0:10]
    
    t=np.arange(1,T+1)

    f1 = plt.figure(1)
    plt.plot(t,result_between[0][:], 'ro-',t,result_degree[0][:], 'bs-',t,result_pagerank[0][:], 'g^-', t,result_random[0][:], 'cd-', t[0:len(selected_nodes_low)],result_selected[0][0:len(selected_nodes_low)], 'mh-')
    plt.figlegend(('Betweenness','Degree','Pagerank','Random','Selected'),loc='right')
    plt.savefig('LowTx_100_greedy_result.pdf')
    
    f2 = plt.figure(2)
    plt.plot(t,result_between[1][:], 'ro-',t,result_degree[1][:], 'bs-',t,result_pagerank[1][:], 'g^-', t,result_random[1][:], 'cd-', t[0:len(selected_nodes_mid)],result_selected[1][0:len(selected_nodes_mid)], 'mh-')
    plt.figlegend(('Betweenness','Degree','Pagerank','Random','Greedy'),loc='right')
    plt.savefig('MidTx_10000_greedy_result.pdf')
        
    f3 = plt.figure(3)
    plt.plot(t,result_between[2][:], 'ro-',t,result_degree[2][:], 'bs-',t,result_pagerank[2][:], 'g^-', t,result_random[2][:], 'cd-', t[0:len(selected_nodes_high)],result_selected[2][0:len(selected_nodes_high)], 'mh-')
    plt.figlegend(('Betweenness','Degree','Pagerank','Random','Selected'),loc='right')
    plt.savefig('HighTx_1000000_greedy_result.pdf')
    
    plt.show()
    
    fig, (ax1, ax2,ax3) = plt.subplots(3, 1,sharex='col', sharey='row',gridspec_kw={'hspace': 0.1})
    fig.suptitle('Betweenness Improvements of Our Node')
    plt.xlabel("The Number of Nodes Connected")
    plt.ylabel("Normalized Betweenness Centrality")
    ax1.plot(t,result_between[0][:], 'ro-',t,result_degree[0][:], 'bs-',t,result_pagerank[0][:], 'g^-', t,result_random[0][:], 'cd-', t[0:len(selected_nodes_low)],result_selected[0][0:len(selected_nodes_low)], 'mh-')
    #ax1.axis([0, 50, -10000, 1100000])
    ax2.plot(t,result_between[1][:], 'ro-',t,result_degree[1][:], 'bs-',t,result_pagerank[1][:], 'g^-', t,result_random[1][:], 'cd-', t[0:len(selected_nodes_mid)],result_selected[1][0:len(selected_nodes_mid)], 'mh-')
    #ax2.axis([0, 50, -10000, 1100000])
    l1,l2,l3,l4,l5=ax3.plot(t,result_between[2][:], 'ro-',t,result_degree[2][:], 'bs-',t,result_pagerank[2][:], 'g^-', t,result_random[2][:], 'cd-', t[0:len(selected_nodes_high)],result_selected[2][0:len(selected_nodes_high)], 'mh-')
    #ax3.axis([0, 50, -10000, 1100000])
    
    plt.figlegend((l1,l2,l3,l4,l5),('Betweenness','Degree','Pagerank','Random','Selected'),loc='lower center',ncol=5)
    plt.savefig('Combined_01_09.pdf')
        
    plt.show()


def ComputeBetweennessResults(ingraph,selected_nodes_all,txValueIndex):
    
    selected_nodes=selected_nodes_all[txValueIndex]
    txValue = txValueSet[txValueIndex]
    graph=copy.deepcopy(ingraph)
    
    ''' Computing the betweenness values for the selected nodes'''
    for K in np.arange(2,len(selected_nodes)+1): # For K=1 there is no path passing through our node
        '''Uncomment the following lines if TxValue Varies '''

        copy_graph=copy.deepcopy(graph)

        if K==2:
            print 'Top 50 nodes having highest betweenness values'
            print TopKBetweennessNodes(graph,50)
            print (np.sort(graph.betweenness(weights='txCost',directed=True)))[-50:][::-1]
            #time3= timeit.default_timer()
            #print "betweenness computation time: ", round(time3-time2,2)
            #print np.array(graph.betweenness(weights='txCost',directed=True))[topk_nodes.astype(int)]
            print 'Top 50 nodes having highest degree values'
            print TopKDegreeNodes(graph,50)
            print (np.sort(graph.degree()))[-50:][::-1]
            #time4= timeit.default_timer()
            #print "betweenness computation time: ", round(time4-time3,2)
            print 'Top 50 nodes having highest pagerank values'
            print TopKPageRankNodes(graph,50)
            print (np.sort(graph.pagerank()))[-50:][::-1]
            #time5= timeit.default_timer()
            #print "betweenness computation time: ", round(time5-time4,2)

        print 'K=',K

        if testFlag==1:
            print graph
            print graph.betweenness(weights='txCost',directed=True)
            print 'txCost: ', graph.es['txCost']
            print 'Capacity: ', graph.es['capacity']
            print 'Base Fee: ', graph.es['base_fee']


        if K<len(selected_nodes)+1:
            if testFlag==-1:
                print '-----------------------'
                print 'Results for Selected Connections'
                print '-----------------------'

            copy_graph.add_vertices(1)
            index=len(copy_graph.vs)
            copy_graph.vs[index-1]['pub_key']='our_node_pk'
            our_node=copy_graph.vs.find(pub_key='our_node_pk')
            Connect2KSelectedNodes(copy_graph,our_node,selected_nodes,K,OurCapacity,our_base_fee,our_fee_rate,txValue)

            if testFlag==1:
                #print 'After our node is added'
                print summary(copy_graph)

            if testFlag==1:
                print 'Top 2K nodes having highest betweenness values'
                top2k_bnodes= TopKBetweennessNodes(copy_graph,2*K)
                print top2k_bnodes
                print np.array(copy_graph.betweenness(weights='txCost',directed=True))[top2k_bnodes.astype(int)]

            result_selected[txValueIndex][K-1] =copy_graph.betweenness(weights='txCost',directed=True)[index-1]

            if testFlag==-1:
                print '-------'
                print result_selected[txValueIndex][K-1]
                print '-------'

            if testFlag==11:
                print 'Ournodes connections: '
                for edge in copy_graph.es.select(_from=index-1):
                    print edge.tuple

        print 'Top 10 betweenness nodes after ', K, ' connections added to our node'
        print TopKBetweennessNodes(copy_graph,10)
        print (np.sort(copy_graph.betweenness(weights='txCost',directed=True)))[-10:][::-1]
        print 'Betweenness of our node: ', result_selected[txValueIndex][K-1]
    
    return copy_graph



'''Main Code '''

selected_nodes_low=[2796,1223,498,3265,3884,2836,2032,4051,2228,2565]

selected_nodes_mid=[2796,1223,1163,498,3265,1589,4051,3246,2087,2032]# 11. : 2228

selected_nodes_high=[2796,1223,1163,222,2745,3884,3265,4209,2087,3540,3690,1039,797,498,4384,408,1440,724]# 2565

selected_nodes_all = [selected_nodes_low,selected_nodes_mid,selected_nodes_high]


txLen = len(txValueSet)

'''BC Computation'''
if BC_computation_flag==1:
    result_selected = np.zeros((txLen,T))

    for txValueIndex in np.arange(0,txLen):
        loaded_graph=load('lngraphv2.txt',format='pickle')
        
        txValue = txValueSet[txValueIndex]
        graph_deleted_edges=CostofTxCuttingEdges(loaded_graph,txValue)
        print summary(loaded_graph)
        print summary(graph_deleted_edges)
        print 'txValue=',txValue
        
        graph_with_channels= ComputeBetweennessResults(graph_deleted_edges,selected_nodes_all,txValueIndex)
            
        our_node=graph_with_channels.vs.find(pub_key='our_node_pk')
        
        graph_with_capacity= DistributeCapacityOverChannels(graph_with_channels,our_node,OurCapacity)
        
        if txValueIndex==0:
            Graph.save(graph_with_capacity,'graph_with_capacity_lowtx.txt',format='pickle')
        if txValueIndex==1:
            Graph.save(graph_with_capacity,'graph_with_capacity_midtx.txt',format='pickle')
        if txValueIndex==2:
            Graph.save(graph_with_capacity,'graph_with_capacity_hightx.txt',format='pickle')
        
        if testFlag==2:
            ournode=graph_with_capacity.vs.find(pub_key='our_node_pk')
            in_edges= np.array( graph_with_capacity.es.select(_to=ournode.index) )
            for edge in in_edges:
                print graph_with_capacity.es[edge.index]['capacity']
            
            
    np.save('SavedGraphData/selected50.npy',result_selected)

''' End of BC Computation '''


#DisplayBetweennessResults()


low_graph=load('graph_with_capacity_lowtx.txt',format='pickle')
mid_graph=load('graph_with_capacity_midtx.txt',format='pickle')
high_graph=load('graph_with_capacity_hightx.txt',format='pickle')


#txAmount=txValueSet[0]
#ournode=low_graph.vs.find(pub_key='our_node_pk')
#CostofTx(low_graph,txAmount)
#out_edges= np.array( low_graph.es.select(_from=ournode.index) )
#for edge in out_edges:
#    ebc=low_graph.es[edge.index]['edgebetweenness']
#    cost=low_graph.es[edge.index]['txCost']
#    capacity=low_graph.es[edge.index]['capacity']
#    print ebc,capacity,cost
#    reward=ebc*cost
#    


#graph=copy.deepcopy(mid_graph)
#ournode=graph.vs.find(pub_key='our_node_pk')
#txAmount=txValueSet[1]
#out_edges= np.array( graph.es.select(_from=ournode.index) )
#
#ER = np.zeros((10,div))
#ER_max = np.zeros((10,div))
#
#edge_index=int(0)
#for edge in out_edges:
#    edge_global=edge
#    
#    
#    for index1 in np.arange(0,div):
#        fee=(ChCost*index1/div)+1
#        print fee
#        graph.es[edge.index]['txCost']=fee
#        #CostofTxCuttingEdges(graph,txAmount)
#        #print 'Before: ', graph.es[edge.index]['edgebetweenness'],graph.es[edge.index]['txCost']
#        UpdateEBC(graph)
#        ER[edge_index][index1]=graph.es[edge.index]['edgebetweenness']*graph.es[edge.index]['txCost']
#        print 'EBC:  ', graph.es[edge.index]['edgebetweenness']
#        ER_max[edge_index][index1]= (ER[edge_index][index1] *((ChCost*(index1+1)/div)+1) )/fee
#        
#        if ER[edge_index][index1]==0:
#            break
#
#    
#    print ER[edge_index]
#    print ER_max[edge_index]
#    edge_index=edge_index+1
#    
#ER_min=ER
#
#print ER_min
#print ER_max

MaximizeChannelReward(1,ChCost)

print maxRewFee
print maxRew

#print '----------'
#
#maxFee=100
#minFee=1
#
#for index1 in np.arange(0,div):
#    print ((maxFee-minFee)*index1/div)+minFee
#
#print ((maxFee-minFee)*(index1+1)/div)+minFee

''' Summary of the graphs'''

#print summary(low_graph)
#ournode=low_graph.vs.find(pub_key='our_node_pk')
#out_edges= np.array( low_graph.es.select(_from=ournode.index) )
#sum1=0
#for edge in out_edges:
#    print low_graph.es[edge.index]['capacity']
#    sum1= sum1 +low_graph.es[edge.index]['capacity']
#print sum1
#
#print summary(mid_graph)
#ournode=mid_graph.vs.find(pub_key='our_node_pk')
#in_edges= np.array( mid_graph.es.select(_to=ournode.index) )
#sum1=0
#for edge in in_edges:
#    print mid_graph.es[edge.index]['capacity']
#    sum1= sum1 +mid_graph.es[edge.index]['capacity']
#print sum1
#
#print summary(high_graph)
#ournode=high_graph.vs.find(pub_key='our_node_pk')
#in_edges= np.array( high_graph.es.select(_to=ournode.index) )
#sum1=0
#for edge in in_edges:
#    print high_graph.es[edge.index]['capacity']
#    sum1= sum1 +high_graph.es[edge.index]['capacity']
#print sum1

#IGRAPH D--- 4619 68749 -- 
#+ attr: pub_key (v), base_fee (e), capacity (e), edgebetweenness (e), fee_rate (e), txCost (e)
#None
#3644643.0
#82639.0
#405583.0
#149480.0
#259659.0
#74940.0
#110926.0
#110357.0
#111531.0
#49871.0
#4999629.0
#IGRAPH D--- 4619 68713 -- 
#+ attr: pub_key (v), base_fee (e), capacity (e), edgebetweenness (e), fee_rate (e), txCost (e)
#None
#3129690.0
#40222.0
#759844.0
#342207.0
#128860.0
#193254.0
#112942.0
#114507.0
#86325.0
#91830.0
#4999681.0
#IGRAPH D--- 4619 32209 -- 
#+ attr: pub_key (v), base_fee (e), capacity (e), edgebetweenness (e), fee_rate (e), txCost (e)
#None
#1807987.0
#7785.0
#1280002.0
#719521.0
#437778.0
#283760.0
#125935.0
#173068.0
#141257.0
#22770.0
#4999863.0

''' End Of Main Code'''

#loaded_graph=load('lngraphv2.txt',format='pickle')
#
#print summary(loaded_graph)
#
#graph_deleted_edges=CostofTxCuttingEdges(loaded_graph,1000000)
#
#print summary(graph_deleted_edges)
#count=0
#for edge in graph_deleted_edges.es:
#        if graph_deleted_edges.is_multiple(edge):
#            if edge.source==1866:
#                print edge.tuple
#            count=count+1
#            
#print count
# There are 3690 multiple edges for Tx=1000000 graph
#out_edges2=np.array( graph_deleted_edges.es.select(_from=1866) )
#
#
#print graph_deleted_edges.es(32176).tuple
#
#for edge in out_edges2:
#    print edge.target

''' Clusters of the graph '''
#cl=graph_new.clusters()
#
#array= np.array( cl.sizes() )
#
#for a in array:
#    if a>1:
#        print a
#
#lcc=cl.giant()
#
#print summary(lcc)

''' analyzing node set 3265-2229,2316,3118,3124,3228 ''' 
#
#loaded_graph=load('lngraphv2.txt',format='pickle')
#print summary(loaded_graph)
#
#loaded_graph.delete_edges(loaded_graph.es.select(capacity_lt=1000000))
#print summary(loaded_graph)
#
#graph=copy.deepcopy(loaded_graph)
#
#print 'Node 2229'
#node1=2229
#in_edges1= np.array( graph.es.select(_to=node1) )
#print 'In: ', in_edges1
#out_edges1=np.array( graph.es.select(_from=node1) )
#print 'Out: ', out_edges1
#all_edges1= np.concatenate( (in_edges1,out_edges1),axis=None )
#
#print 'Node 3265'
#node2=3265
#in_edges2= np.array( graph.es.select(_to=node2) )
#print 'In: ', in_edges2
#out_edges2=np.array( graph.es.select(_from=node2) )
#print 'Out: ', out_edges2
#all_edges2= np.concatenate( (in_edges2,out_edges2),axis=None )
#
#for edge in in_edges2:
#    print edge.source
#
#print 'Node 2316'
#node2=2316
#in_edges2= np.array( graph.es.select(_to=node2) )
#print 'In: ', in_edges2
#out_edges2=np.array( graph.es.select(_from=node2) )
#print 'Out: ', out_edges2
#all_edges2= np.concatenate( (in_edges2,out_edges2),axis=None )
#
#
#print 'Node 3228'
#node2=3228
#in_edges2= np.array( graph.es.select(_to=node2) )
#print 'In: ', in_edges2
#out_edges2=np.array( graph.es.select(_from=node2) )
#print 'Out: ', out_edges2
#all_edges2= np.concatenate( (in_edges2,out_edges2),axis=None )
#
#
#print 'Node 3124'
#node2=3124
#in_edges2= np.array( graph.es.select(_to=node2) )
#print 'In: ', in_edges2
#out_edges2=np.array( graph.es.select(_from=node2) )
#print 'Out: ', out_edges2
#all_edges2= np.concatenate( (in_edges2,out_edges2),axis=None )
#
#
#print 'Node 3118'
#node2=3118
#in_edges2= np.array( graph.es.select(_to=node2) )
#print 'In: ', in_edges2
#out_edges2=np.array( graph.es.select(_from=node2) )
#print 'Out: ', out_edges2
#all_edges2= np.concatenate( (in_edges2,out_edges2),axis=None )
 
''' General Graph Notes'''
#DisplayBetweennessResults()

#txValue = txValueSet[txValueIndex]
#print 'txValue=',txValue
#loaded_graph=load('lngraphv2.txt',format='pickle')
#graph=copy.deepcopy(loaded_graph)
#CostofTx(graph,txValue)
#print summary(graph)
#
#graph.add_vertices(1)
#index=len(graph.vs)
#graph.vs[index-1]['pub_key']='our_node_pk'
#ournode=graph.vs.find(pub_key='our_node_pk')
#Connect2KSelectedNodes(graph,ournode,selected_nodes,len(selected_nodes),OurCapacity,our_base_fee,our_fee_rate,txValue)
#
#ournode=graph.vs.find(pub_key='our_node_pk')
#in_edges= np.array( graph.es.select(_to=ournode.index) )
#print in_edges
#out_edges=np.array( graph.es.select(_from=ournode.index) )
#all_edges= np.concatenate( (in_edges,out_edges),axis=None )
#
#for edge in in_edges:
#    edgeIndex=edge.index
#    graph.es[edgeIndex]['base_fee']=def_base_fee
#    graph.es[edgeIndex]['fee_rate']=def_fee_rate
#print in_edges
#CostofTx(graph,txValue)
#
#
#new_graph=DistributeCapacityOverChannels(graph,ournode,selected_nodes,OurCapacity)
#
#print summary(graph)
#print summary(new_graph)
#print ournode
#
##print all_edges
#for edge in all_edges:
#    edgeIndex=edge.index
#    print new_graph.es[edgeIndex]['capacity']


'''Computing default values for base_fee and fee_rate'''
#bf=np.array(graph.es['base_fee'])
#counts_bf=np.bincount(bf)
#print np.argmax(counts_bf)
#
#fr=np.array(graph.es['fee_rate'])
#counts_fr=np.bincount(fr)
#print np.argmax(counts_fr)

#tcapacity=0
#for edge in all_edges:
#    edgeIndex=edge.index
#    tcapacity=tcapacity+ new_graph.es[edgeIndex]['capacity']
#
#print tcapacity



#degree_array=np.array( graph.degree() )
#
#counter=0
#counter2=0
#counter4=0
#counter6=0
#
#for kk in np.arange(0,len(degree_array)):
#    if degree_array[kk]==0:
#        counter=counter+1
#    elif degree_array[kk]<=2:
#        counter2=counter2+1
#    elif degree_array[kk]<=4:
#        counter4=counter4+1
#    elif degree_array[kk]<=6:
#        counter6=counter6+1
#
#print '# of degree 0: ', counter
#print '# of degree 1,2: ', counter2
#print '# of degree 3,4: ', counter4
#print '# of degree 5,6: ', counter6
# # of degree 0:  120
# # of degree 1,2:  1084
# # of degree 3,4:  588
# # of degree 5,6:  382
