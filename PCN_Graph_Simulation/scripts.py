from igraph import *
import json

import numpy as np
import copy
import random
import timeit

import matplotlib.pyplot as plt


HighValue=111111111111
OurCapacity=100000000
our_base_fee=1
our_fee_rate=1

def_fee_rate=1
def_base_fee=1000
#txValue=1000
txValueSet=[100,10000,1000000]

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

#def Connect2TopKBetweennessNodes(graph,node,k,capacity,txAmount):
#    topk_nodes=TopKBetweennessNodes(graph,k)
#    Ch_capacity=int(capacity/k)
#    for target in topk_nodes:
#        CreateChannel(graph,node,target,Ch_capacity,our_base_fee,our_fee_rate,txAmount)

# def Connect2RandomKNodes(graph,node,k,capacity):
#     random_nodes=random.sample(range(0,len(graph.vs)-2),k)
#     Ch_capacity=int(capacity/k)
#     for target in random_nodes:
#         CreateChannel(graph,node,target,Ch_capacity,our_base_fee,our_fee_rate,txValue)


#def Connect2SecondTopKBetweennessNodes(graph,node,k,capacity,txAmount):
#    topk_nodes=TopKBetweennessNodes(graph,2*k)[k:]
#    Ch_capacity=int(capacity/k)
#    for target in topk_nodes:
#        CreateChannel(graph,node,target,Ch_capacity,our_base_fee,our_fee_rate,txAmount)
#
#def Connect2TopKDegreeNodes(graph,node,k,capacity,txAmount):
#    topk_nodes=TopKDegreeNodes(graph,k)
#    Ch_capacity=int(capacity/k)
#    for target in topk_nodes:
#        CreateChannel(graph,node,target,Ch_capacity,our_base_fee,our_fee_rate,txAmount)
#
#def Connect2TopKPageRankNodes(graph,node,k,capacity,txAmount):
#    topk_nodes=TopKPageRankNodes(graph,k)
#    Ch_capacity=int(capacity/k)
#    for target in topk_nodes:
#        CreateChannel(graph,node,target,Ch_capacity,our_base_fee,our_fee_rate,txAmount)
#
#def Connect2KRandomNodes(graph,node,k,capacity,txAmount):
#    Ch_capacity=int(capacity/k)
#    #print randomk_nodes[0:k]
#    for target in random_nodes[0:k]:
#        CreateChannel(graph,node,target,Ch_capacity,our_base_fee,our_fee_rate,txAmount)
#
#def Connect2KSelectedNodes(graph,node,k,capacity,txAmount):
#    Ch_capacity=int(capacity/k)
#    #print randomk_nodes[0:k]
#    for target in selected_nodes[0:k]:
#        CreateChannel(graph,node,target,Ch_capacity,our_base_fee,our_fee_rate,txAmount)
        
def Connect2KNodes(graph,node,k,capacity,txAmount,connecting_nodes):
    Ch_capacity=int(capacity/k)
    #print randomk_nodes[0:k]
    for target in connecting_nodes[0:k]:
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

loaded_graph=load('lngraphv2.txt',format='pickle')

random_nodes=random.sample( range(len(loaded_graph.vs)),T)# To keep the random nodes consistent

selected_nodes=[2796,1223,1163,498,3265,1589,4051,3246,2087,2032,3884,2836,2228,2565,222,797,2745,4209]

print summary(loaded_graph)

#edgelist1=loaded_graph.es.select(capacity_gt=1000000)
#print len(edgelist1)
#
#for ed in np.arange(55550,55600):
#    print loaded_graph.es[ed]['capacity']

txLen = len(txValueSet)

result_between = np.zeros((txLen,T))
result_degree = np.zeros((txLen,T))
result_pagerank = np.zeros((txLen,T))
result_random = np.zeros((txLen,T))
result_selected = np.zeros((txLen,T))

for txValueIndex in np.arange(0,txLen):

    txValue = txValueSet[txValueIndex]
    print 'txValue=',txValue
    
    graph_deleted_edges=CostofTxCuttingEdges(loaded_graph,txValue)
    print summary(graph_deleted_edges)
    
    topbetweenness_nodes=TopKBetweennessNodes(graph_deleted_edges,T)
    topdegree_nodes=TopKDegreeNodes(graph_deleted_edges,T)
    toppagerank_nodes=TopKPageRankNodes(graph_deleted_edges,T)

    print 'Top nodes having highest betweenness values'
    print topbetweenness_nodes
    print (np.sort(graph_deleted_edges.betweenness(weights='txCost',directed=True)))[-T:][::-1]
    #time3= timeit.default_timer()
    #print "betweenness computation time: ", round(time3-time2,2)
    #print np.array(graph.betweenness(weights='txCost',directed=True))[topk_nodes.astype(int)]
    print 'Top nodes having highest degree values'
    print topdegree_nodes
    print (np.sort(graph_deleted_edges.degree()))[-T:][::-1]
    #time4= timeit.default_timer()
    #print "betweenness computation time: ", round(time4-time3,2)
    print 'Top nodes having highest pagerank values'
    print toppagerank_nodes
    print (np.sort(graph_deleted_edges.pagerank()))[-T:][::-1]
    #time5= timeit.default_timer()
    #print "betweenness computation time: ", round(time5-time4,2)


    #CostofTx(graph,txValue)
    #graph=copy.deepcopy(loaded_graph)
    #CostofTx(graph,txValue)
    for K in np.arange(2,T+1): # For K=1 there is no path passing through our node
         # Updating the weights according to TxValue

        copy_graph=copy.deepcopy(graph_deleted_edges)
        copy_graph2=copy.deepcopy(graph_deleted_edges)
        copy_graph3=copy.deepcopy(graph_deleted_edges)
        copy_graph4=copy.deepcopy(graph_deleted_edges)
        copy_graph5=copy.deepcopy(graph_deleted_edges)
        
        

        print 'K=',K
        #graph=copy.deepcopy(loaded_graph)
        #CostofTx(g,txValue)
        #print 'loaded graph: ', summary(loaded_graph)

        #time2= timeit.default_timer()

        #print "graph generation time: ", round(time2-time1,2)

        #print summary(graph)
        if testFlag==1:
            print copy_graph
            print copy_graph.betweenness(weights='txCost',directed=True)
            print 'txCost: ', graph.es['txCost']
            print 'Capacity: ', graph.es['capacity']
            print 'Base Fee: ', graph.es['base_fee']


        if testFlag==-1:
            print '-----------------------'
            print 'Results for KTop Betweenness Connections'
            print '-----------------------'

        copy_graph.add_vertices(1)
        index=len(copy_graph.vs)
        copy_graph.vs[index-1]['pub_key']='our_node_pk'
        our_node=copy_graph.vs.find(pub_key='our_node_pk')
        
        Connect2KNodes(copy_graph,our_node,K,OurCapacity,txValue,topbetweenness_nodes)

        if testFlag==11:
            #print 'After our node is added'
            print summary(copy_graph)

        if testFlag==1:
            print copy_graph.betweenness(weights='txCost',directed=True)

        if testFlag==1:
            print 'Top 2K nodes having highest betweenness values'
            top2k_bnodes= TopKBetweennessNodes(copy_graph,2*K)
            print top2k_bnodes
            print np.array(copy_graph.betweenness(weights='txCost',directed=True))[top2k_bnodes.astype(int)]

        result_between[txValueIndex][K-1] = copy_graph.betweenness(weights='txCost',directed=True)[index-1]

        if testFlag==-1:
            print '-------'
            print result_between[txValueIndex][K-1]
            print '-------'

        if testFlag==-1:
            print 'Ournodes connections: '
            for edge in copy_graph.es.select(_from=index-1):
                print edge.tuple

        if testFlag==-1:
            print '-----------------------'
            print 'Results for KTop Degree Connections'
            print '-----------------------'

        copy_graph2.add_vertices(1)
        index=len(copy_graph2.vs)
        copy_graph2.vs[index-1]['pub_key']='our_node_pk'
        our_node=copy_graph2.vs.find(pub_key='our_node_pk')
        Connect2KNodes(copy_graph2,our_node,K,OurCapacity,txValue,topdegree_nodes)

        if testFlag==11:
            #print 'After our node is added'
            print summary(copy_graph2)

        if testFlag==1:
            print 'Top 2K nodes having highest betweenness values'
            top2k_bnodes= TopKBetweennessNodes(copy_graph2,2*K)
            print top2k_bnodes
            print np.array(copy_graph2.betweenness(weights='txCost',directed=True))[top2k_bnodes.astype(int)]

        result_degree[txValueIndex][K-1] = copy_graph2.betweenness(weights='txCost',directed=True)[index-1]

        if testFlag==-1:
            print '-------'
            print result_degree[txValueIndex][K-1]
            print '-------'

        if testFlag==-1:
            print 'Ournodes connections: '
            for edge in copy_graph2.es.select(_from=index-1):
                print edge.tuple

        if testFlag==-1:
            print '-----------------------'
            print 'Results for KTop PageRank Connections'
            print '-----------------------'

        copy_graph3.add_vertices(1)
        index=len(copy_graph3.vs)
        copy_graph3.vs[index-1]['pub_key']='our_node_pk'
        our_node=copy_graph3.vs.find(pub_key='our_node_pk')
        Connect2KNodes(copy_graph3,our_node,K,OurCapacity,txValue,toppagerank_nodes)

        if testFlag==11:
            #print 'After our node is added'
            print summary(copy_graph3)

        if testFlag==1:
            print 'Top 2K nodes having highest betweenness values'
            top2k_bnodes= TopKBetweennessNodes(copy_graph3,2*K)
            print top2k_bnodes
            print np.array(copy_graph3.betweenness(weights='txCost',directed=True))[top2k_bnodes.astype(int)]

        result_pagerank[txValueIndex][K-1] =copy_graph3.betweenness(weights='txCost',directed=True)[index-1]

        if testFlag==-1:
            print '-------'
            print result_pagerank[txValueIndex][K-1]
            print '-------'

        if testFlag==-1:
            print 'Ournodes connections: '
            for edge in copy_graph3.es.select(_from=index-1):
                print edge.tuple

        if testFlag==-1:
            print '-----------------------'
            print 'Results for K Random Connections'
            print '-----------------------'

        copy_graph4.add_vertices(1)
        index=len(copy_graph4.vs)
        copy_graph4.vs[index-1]['pub_key']='our_node_pk'
        our_node=copy_graph4.vs.find(pub_key='our_node_pk')
        Connect2KNodes(copy_graph4,our_node,K,OurCapacity,txValue,random_nodes)

        if testFlag==11:
            #print 'After our node is added'
            print summary(copy_graph4)

        if testFlag==1:
            print 'Top 2K nodes having highest betweenness values'
            top2k_bnodes= TopKBetweennessNodes(copy_graph4,2*K)
            print top2k_bnodes
            print np.array(copy_graph4.betweenness(weights='txCost',directed=True))[top2k_bnodes.astype(int)]

        result_random[txValueIndex][K-1] =copy_graph4.betweenness(weights='txCost',directed=True)[index-1]

        if testFlag==-1:
            print '-------'
            print result_random[txValueIndex][K-1]
            print '-------'

        if testFlag==-1:
            print 'Ournodes connections: '
            for edge in copy_graph4.es.select(_from=index-1):
                print edge.tuple

        if K<len(selected_nodes)+1:
            if testFlag==-1:
                print '-----------------------'
                print 'Results for Selected Connections'
                print '-----------------------'

            copy_graph5.add_vertices(1)
            index=len(copy_graph5.vs)
            copy_graph5.vs[index-1]['pub_key']='our_node_pk'
            our_node=copy_graph5.vs.find(pub_key='our_node_pk')
            Connect2KNodes(copy_graph5,our_node,K,OurCapacity,txValue,selected_nodes)

            if testFlag==1:
                #print 'After our node is added'
                print summary(copy_graph5)

            if testFlag==1:
                print 'Top 2K nodes having highest betweenness values'
                top2k_bnodes= TopKBetweennessNodes(copy_graph5,2*K)
                print top2k_bnodes
                print np.array(copy_graph5.betweenness(weights='txCost',directed=True))[top2k_bnodes.astype(int)]

            result_selected[txValueIndex][K-1] =copy_graph5.betweenness(weights='txCost',directed=True)[index-1]

            if testFlag==-1:
                print '-------'
                print result_selected[txValueIndex][K-1]
                print '-------'

            if testFlag==-1:
                print 'Ournodes connections: '
                for edge in copy_graph5.es.select(_from=index-1):
                    print edge.tuple

print 'Highest Betweenness'
print result_between

np.save('SavedGraphData/between50.npy',result_between)

print 'Highest Degree'
print result_degree

np.save('SavedGraphData/degree50.npy',result_degree)

print 'Highest PageRank'
print result_pagerank

np.save('SavedGraphData/pagerank50.npy',result_pagerank)

print 'Random'
print result_random

np.save('SavedGraphData/random50.npy',result_random)

print 'Selected'
print result_selected

np.save('SavedGraphData/selected50.npy',result_selected)

#result_between=np.array([[      0.  ,             0.       ,        0.       , 1165725.07598197,
#  1167272.35751702 ,1167597.1585423,  1167999.15397879 ,1686897.5939993,
#  1687700.96121592, 1688187.24235401],
# [      0.   ,            0.  ,          3436.43196913 ,   7799.52712637,
#  1218687.87781938, 1221677.02387763, 1224363.69609095, 1233487.02375474,
#  1773068.61582286, 1776237.5390844 ],
# [      0.    ,           0.     ,          0.   ,      1218330.01894219,
#  1218398.54449844, 1218456.28981728, 1760601.6172163,  1760634.85552035,
#  1760654.83467802, 1760691.04738908]])
#
#
#result_degree=np.array([[      0.     ,    1163253.99098287 ,1165095.77099952, 1683390.52555532,
#  1684266.70940144 ,1685935.07373123, 1686405.12433536 ,1687416.14914985,
#  1688603.430077 ,  1865892.34747832],
# [      0.       ,  1200475.35673782 ,1206360.72516717, 1742687.11385433,
#  2037183.7889861  ,2044055.29100219 ,2047679.31952628, 2057663.85632269,
#  2066138.75650401 ,2246791.55866431],
# [      0.     ,    1213853.13434509, 1214729.76306572, 1756898.00099004,
#  2041348.18703715 ,2048217.26542784, 2048234.12223173, 2048354.07711504,
#  2136585.52566274, 2313269.52520625]])
#
#
#
#result_pagerank=np.array([[      0.    ,     1163253.99098287 ,1165095.77099952, 1683390.52555532,
#  1684266.70940144 ,1685935.07373123, 1686901.14544626, 1864070.53181223,
#  1864617.70741795, 1865892.34747832],
# [      0.       ,  1200475.35673782, 1206360.72516717 ,1742687.11385433,
#  2037183.7889861 , 2044055.29100219 ,2053271.65191637, 2233229.09464227,
#  2237854.16001152 ,2246791.55866431],
# [      0.        , 1213853.13434509, 1214729.76306572, 1756898.00099004,
#  2041348.18703715 ,2048217.26542784 ,2048337.25061419, 2225021.25015769,
#  2225038.07665855 ,2313269.52520625]])
#
#
#result_random=np.array([[    0.     ,     8794.    ,     13288.40572459, 17765.91346269,
#  22243.65139982, 26728.72958982 ,35405.72958982 ,44202.32244696,
#  48683.76166431, 53160.10815699],
# [    0.       ,   8825.   ,      17612.  ,       22108.96460003,
#  26594.24836124 ,32114.54493771, 40790.54493771 ,49587.75922342,
#  58397.92987733, 62938.25606554],
# [    0.      ,    8825.   ,      17609.    ,     26365.,
#  30840.   ,      42966.60925513 ,51638.60925513, 60429.80925513,
#  69239.80925513, 73797.10044803]])

# Best Improvements LowTx:
#Betweenness: 4,8: 1628- 2796,235
#Degree: 2,4,10: 1223- 2796,235,4083
#PageRank:2,4,8: 2796- 1223,235,4083

# Best Improvements MidTx:
#Betweenness: 5,9,12: 1628- 2796,235
#Degree: 2,4,5,10: 1223- 2796,235,1163,4083
#PageRank:2,4,5,8: 2796- 1223,235,1163,4083

# Best Improvements HighTx:
#Betweenness: 4,7: 1628- 2796,235
#Degree: 2,4,5,9,10: 1223- 2796,1163,797,4083
#PageRank:2,4,5,8,10: 2796- 1223,235,1163,4083,797

# our_list= 2796,1223,235,1163,4083,797

''' Plotting result '''

result_between = np.load('SavedGraphData/between50.npy')
result_degree = np.load('SavedGraphData/degree50.npy')
result_pagerank = np.load('SavedGraphData/pagerank50.npy')
result_selected = np.load('SavedGraphData/selected50.npy')



t=np.arange(1,T+1)

f1 = plt.figure(1)
plt.plot(t,result_between[0][:], 'ro-',t,result_degree[0][:], 'bs-',t,result_pagerank[0][:], 'g^-', t,result_random[0][:], 'cd-', t[0:len(selected_nodes)],result_selected[0][0:len(selected_nodes)], 'mh-')
plt.figlegend(('Betweenness','Degree','Pagerank','Random','Selected'),loc='right')
plt.savefig('LowTx_28_08.pdf')

f2 = plt.figure(2)
plt.plot(t,result_between[1][:], 'ro-',t,result_degree[1][:], 'bs-',t,result_pagerank[1][:], 'g^-', t,result_random[1][:], 'cd-', t[0:len(selected_nodes)],result_selected[1][0:len(selected_nodes)], 'mh-')
plt.figlegend(('Betweenness','Degree','Pagerank','Random','Selected'),loc='right')
plt.savefig('MidTx_28_08.pdf')

f3 = plt.figure(3)
plt.plot(t,result_between[2][:], 'ro-',t,result_degree[2][:], 'bs-',t,result_pagerank[2][:], 'g^-', t,result_random[2][:], 'cd-', t[0:len(selected_nodes)],result_selected[2][0:len(selected_nodes)], 'mh-')
plt.figlegend(('Betweenness','Degree','Pagerank','Random','Selected'),loc='right')
plt.savefig('HighTx_28_08.pdf')

plt.show()
