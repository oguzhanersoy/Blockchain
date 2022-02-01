from igraph import *
import timeit
import random
import numpy as np


# g_er_50 = Graph.Erdos_Renyi(50,0.5,directed=False)
# while (g_er_50.is_connected()==False):
#    g_er_50 = Graph.Erdos_Renyi(50,0.5,directed=False)
# print '50 node ER Graph',g_er_50
# g= Graph.Barabasi(100,8,directed=False,outpref=True,start_from=g_er_50)

# g=Graph.Barabasi(1000,3,directed=False,outpref=True)
#print '40 node BA Graph',g

# neighborsOfClient=g.neighbors(39,mode=ALL)
# nb=neighborsOfClient[0]

#print g.get_shortest_paths(39, to=20, mode=ALL)

# print g.is_weighted()
# g.es["weight"]=1.0
# print g.is_weighted()
# print 'Adj', g.adjacent(39)
# print 'Adj', g.adjacent(0)



#print "Without weights:", g.get_shortest_paths(39, to=20, mode=ALL)

#print "With weights:", g.get_shortest_paths(39, to=20, mode=ALL,weights="weight")

#print g.es["weight"]

#

#start= timeit.default_timer()

#g=Graph.Barabasi(5000,15,directed=False,outpref=True)

# for edge in g.es:
#    edge["weight"] = 1+ random.randint(15,50)
#
# stop = timeit.default_timer()
# time= round(stop-start,2)
#
# print "Generating time:", time
#
# # print g
#
# start2= timeit.default_timer()
#
# btw=g.betweenness(weights="weight",directed=False)
#
# stop2 = timeit.default_timer()
# time2= round(stop2-start2,2)
#
# print "Betweenness time:", time2
# # print g.betweenness()
#
# print btw[1:10]
# print btw[990:999]


g=Graph.Barabasi(20,3,directed=True,outpref=True)

print g

print g.vs[14]

index=len(g.es)
g.add_edges([(0,14)])
g.es[index]['capacity']=10

print g
print g.es['capacity']


g.vs['btw']= g.betweenness()

print g.vs['btw']

topk=np.array([1 ,5,19])


print np.array(g.vs['btw'])[topk.astype(int)]
