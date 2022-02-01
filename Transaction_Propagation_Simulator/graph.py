from igraph import *
import timeit
import random


numberOfTest = 1000

#numberOfNodes = 2000
#numberOfConnections = 8
#edgeProb = float(numberOfConnections) / float(numberOfNodes)

#g= Graph()
#
#g_er = Graph.Erdos_Renyi(numberOfNodes,edgeProb,directed=False)
#
##print(g_er)
#
#g= Graph.Barabasi(numberOfNodes,numberOfConnections,directed=False,outpref=True)
#
#g_full= Graph.Full(30)
#
#g_ba2= Graph.Barabasi(numberOfNodes,numberOfConnections,directed=False,outpref=True,start_from=g_full)
#
##print(g)
#
#a=Graph.degree(g)
#print(a[1:250])
#
#print('Average Path length of BA:')
#print(g.average_path_length(directed=False))
#
#c=Graph.degree(g_ba2)
#print(c[1:250])
#
#print('Average Path length of BA2:')
#print(g_ba2.average_path_length(directed=False))
#
#print(g_er.is_connected())
#
#b=Graph.degree(g_er)
#print(b[1:250])
#
#print('Average Path length of ER:')
#print(g_er.average_path_length(directed=False))
#Graph.__plot__(g,)
#
def ListSorting(list):
    tempList=list
    lenList=[]
    for x in range(0,len(list)):
        lenList.append(len(list[x]))
    lenList.sort()
#    print lenList
#    print 'List:',list

    for sp in range (0, len(list)-1 ):
        for lp in range (sp+1, len(list) ):
            if(len(list[lp])<len(list[sp])):
                temp1=list[sp]
                list[sp]=list[lp]
                list[lp]=temp1

#    print 'List:',list
    return list



#list=[[1,2,3],[5,6],[0,2,5,6],[3,4,5],[9,3,0],[8,0]]

#ListSorting(list)

def Reachability(paths,connects):
    failprob = [2, 3, 4]
    redundantShift = [0,2,5] # to make sure the failings are relatively independent since they look for different parts
    reachable=[0]*3
    for re in range(0,3):
#        print 're:',re
        for p in range(0,connects):
#            print 'p=',p
            temp=1
            for j in range(1,len(paths[p])):
#                if(paths[p][j]>=10):
                if( (paths[p][j]-redundantShift[re])%10 < failprob[re]):
                    temp=0
#            print 'temp=',temp
            if(temp==1):
                reachable[re]=1
                break
#    for re in range(0,3):
#        if (reachable[re]==0):
#            print failprob[re],failprob[re],failprob[re], paths
    return reachable

#paths=[[55, 32],[55, 8, 12],[55, 2, 21],[55, 3, 92], [55,7,6]]
#
#print Reachability(paths,4,2)
#print Reachability(paths,4)
#print Reachability(paths,4,4)
#print Reachability(paths,4,5)
#
#
#paths=[[36, 12, 8], [36, 35, 24], [36, 35, 27], [36, 12, 34, 11]]
#print Reachability(paths,4)
#paths=[[36, 1, 8], [36, 35, 21], [36, 31, 27], [36, 12, 34, 11],[36,46]]
#print Reachability(paths,4)
#paths=[[36, 12, 8], [36, 37, 24], [36, 35, 26], [36, 2, 0, 3]]
#print Reachability(paths,4)
###
def numberOfVisitedNodes(g):
    leader= random.randint(0,g.vcount()-1)
#    print 'Leader node:', leader
    reach=[0]*3
    for tr in range(1,numberOfTransactions+1):
        client= random.randint(0,g.vcount()-1)
        while client == leader:
            client= random.randint(0,g.vcount()-1)
#        print 'Client node:', client
        neighborsOfClient=g.neighbors(client,mode=ALL)
#        print 'Neighbors:',neighborsOfClient
#        AllShortestPaths=g.get_all_shortest_paths(leader, to=client, mode=ALL)
#        print 'Shortest Paths from client to leader:',AllShortestPaths

        ShortestPaths=[]
        for nb in neighborsOfClient:
            TempPaths=g.get_all_shortest_paths(leader, to=nb, mode=ALL)
            ShortestPaths.append(random.choice(TempPaths))
#        print 'Gradients are determined', timeit.default_timer()
        nodeSet=set()

        ShortestPaths=ListSorting(ShortestPaths)
#        print 'PATHS:',ShortestPaths
        reach=Reachability(ShortestPaths,numberOfConnections)
#        print 'Failing Prob. is calculated', timeit.default_timer()
        reach2[tr-1]=reach[0]
        reach3[tr-1]=reach[1]
        reach4[tr-1]=reach[2]
        #print 'Connections:',numberOfConnections, 'Nodes:', numberOfNodes
#        print 'Client:',client
        for nb in range (0, numberOfConnections):
#            print 'PATH:',ShortestPaths[nb]
            for i in range(0,len(ShortestPaths[nb])):
                nodeSet.add(ShortestPaths[nb][i])
        
#        print 'nodeSet:',nodeSet
        numNodes.append(nodeSet)
        lenNodes.append(len(nodeSet))
    return reach2,reach3,reach4
#  print len(ShortestPaths)#, AllShortestPaths, AllShortestPaths[0][1]



#nodeSet = (50,50,100,100,500,500,500,1000,1000,1000,2000,2000,5000,5000,10000,10000,20000,20000,50000,50000)
#conSet =  (4, 8, 4,  8,  4,  8,  16, 4,   8,   16,  8,   16,  8,   16,  8,    16,   8,    16,   8,    16)
nodeSet = (1000,2000,200,200,500,10000,10000,500,1000,1000,500,1000,1000,1000,2000,2000,5000,5000,10000,10000,20000,20000,50000,50000)
conSet =  (16,  16, 8,  16, 16, 8, 16,  4,  4,  16,  16, 4,   8,   16,  8,   16,  8,   16,  8,    16,   8,    16,   8,    16)
g_full_20= Graph.Full(20)
g_full_10= Graph.Full(10)

with open('workfile','a') as f:
    f.write(str('\n Number of Trials: %s\n' % numberOfTest))
    numberOfTransactions=100;
    f.write(str('Number of Transactions:%s \n' % numberOfTransactions))
    failprobability = [2, 3, 4]
    reach2=[0]*numberOfTransactions
    reach3=[0]*numberOfTransactions
    reach4=[0]*numberOfTransactions

#    f.write(str('\n Node Failing Probability: %s \n' % float(failpr/10.0)))

#        print '\n'
    for param in range(1,3):
        numNodes=[]
        lenNodes=[]

        numberOfNodes=nodeSet[param-1]
        numberOfConnections=conSet[param-1]
    #    numberOfNodes = 500
    #    numberOfConnections = 8
    #    numberOfTransactions=numberOfNodes/5
        start = timeit.default_timer()
        average= 0.0
        sumNodes=0.0
        failures=[0]*3
        failingPathRatio=0.0

        for test in range(1,numberOfTest+1):
            if test % 100 == 0 :
                print test, 'tests are done.'

#            edgeProb = float(numberOfConnections) / float(numberOfNodes)
#            print timeit.default_timer()
            g_er_50 = Graph.Erdos_Renyi(50,0.5,directed=False)
            while (g_er_50.is_connected()==False):
                g_er_50 = Graph.Erdos_Renyi(50,0.5,directed=False)
#           degree(vertices, mode=ALL, loops=True)


#            print g_er_50
#            print timeit.default_timer()
            g= Graph.Barabasi(numberOfNodes,numberOfConnections,directed=False,outpref=True,start_from=g_er_50)
            while(min(g.degree(g.vs, mode=ALL, loops=True))<numberOfConnections):
               g= Graph.Barabasi(numberOfNodes,numberOfConnections,directed=False,outpref=True,start_from=g_er_50)

#            print 'Graph is generated\n', timeit.default_timer()
            average+=g.average_path_length(directed=False)
#            print 'Average Path is calculated', timeit.default_timer()
            reach=numberOfVisitedNodes(g)
            sumNodes+=sum(lenNodes)/len(lenNodes)
            for alpha in range(0,3):
                failures[alpha]+=len(reach[alpha])-sum(reach[alpha])

        average/=numberOfTest

        sumNodes/=numberOfTest
#        failingPathRatio=failures/float(numberOfTest)

        stop = timeit.default_timer()
        time= round(stop-start,2)
        print str('Parameters: %s - %s (Time %s sec)' % (numberOfNodes,numberOfConnections,time) )
        f.write(str('Parameters: %s - %s (Time %s sec) \n' % (numberOfNodes,numberOfConnections,time) ))
        f.write(str('Average Path Length: %s \n' % average))
        print str('Average Path Length: %s' % average)
        f.write(str('Average Nodes Visited: %s \n' % sumNodes))
        print str('Average Nodes Visited: %s' % sumNodes)
        f.write(str('Total Failing Paths: [0.2, 0.3, 0.4] -> %s \n' %failures))
        print 'Failures:', failures, '\n'
    #    print 'Total transactions:',numberOfTest*numberOfTransactions
    #    print 'Failing ones:', failures
#            print '\n'
#        print g
f.close()



#g_er_50 = Graph.Erdos_Renyi(50,0.5,directed=False)
#while (g_er_50.is_connected()==False):
#    g_er_50 = Graph.Erdos_Renyi(50,0.5,directed=False)
#print '50 node ER Graph',g_er_50
#g= Graph.Barabasi(100,8,directed=False,outpref=True,start_from=g_er_50)
#print '100 node BA Graph',g
#
#neighborsOfClient=g.neighbors(99,mode=ALL)
#nb=neighborsOfClient[0]
#
#print g.get_shortest_paths(99, to=80, mode=ALL)
#
#print g.is_weighted()
#g.es["weight"]=1.0
#print g.is_weighted()
#print 'Adj', g.adjacent(99)
#
#for edge in g.adjacent(99):
#    edge = 1+ random.randint(15,22)
#
#
#print g.get_shortest_paths(99, to=80, mode=ALL)



