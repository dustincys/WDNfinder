#!/usr/bin/env python
# encoding: utf-8
'''
# =============================================================================
#      FileName: structuralcontrol.py
#          Desc:
#        Author: Chu Yanshuo
#         Email: chu@yanshuo.name
#      HomePage: http://yanshuo.name
#       Version: 0.0.1
#    LastChange: 2015-12-22 11:42:44
#       History:
# =============================================================================
'''
"""
attribute appened:
    node: class label
    edge: class label mark
"""
# Copyright (C) by
# Chu Yanshuo <chu@yanshuo.name>
# All rights reserved
import networkx
import copy
import random
import Queue

class StructuralControl:

    """Docstring for BipartiteGraph. """

    def __init__(self, directedGraph, bipartite):
        self.DG = directedGraph
        self.bipartite = bipartite

    def samplingWeight(self, times):
        """Sampling the MCM of GcsP
            The GcsP is saved by pickle in the file of inFilePath,
            the sampling result is saved in file of outFilePath

        :times: Sampling times
        :inFilePath: GcsP file
        :outFilePath: Sampling result file
        :returns: None

        """
        self.__matchNetwork(self.bipartite)
        self.__classifyEdges(self.bipartite)
        self.__classifyNodes(self.bipartite)
        self.__sampling(times, self.bipartite)

    def __classifyNodes(self, tempG):
        """classify nodes into 3 classes: critical, intermittent, redundant.
        :returns: @todo
        """
        #here, the GcsP has trimed some edges, which means, some nodes in GcsP have no predecessors
        for nd in self.DG.nodes():
            # change self.DG.predecessors(nd) to tempG.neighbors("{}\t-".format(nd))
            if len(tempG.neighbors("{}\t-".format(nd)))==0:
                self.DG.node[nd]['class']='critical'
            else:
                self.DG.node[nd]['class']='intermittent'

        matchedNodes=filter(lambda res: res[1]['label']=='matched', tempG.nodes(data=True))
        for (nd,att) in matchedNodes:
            if nd.endswith("\t-"):
                nodei=nd
                nodej=filter(lambda res: tempG.edge[nd][res]['label']=="matching", tempG.neighbors(nd))[0]
                tempBiG=copy.deepcopy(tempG)
                tempBiG.remove_node(nd)
                flag=self.__BFS_classifyNodes(tempBiG, nodej)
                if not flag:
                    self.DG.node[nd.strip("\t-")]['class']='redundant'
        pass

    def __classifyEdges(self, tempG):
        """link classification
        :returns: @todo

        """
        Gd1, Gd2 = self.__turnMatchedGp2Gd(tempG)

        #get all the free nodes in Gp (self.BiG)
        freeNodes = filter(lambda res: res[1]['label']=='free', tempG.nodes(data=True))
        for node in freeNodes:
            nodeName = node[0]
            for Gd in [Gd1,Gd2]:
                flag, pathlist = self.__BFS_classifyEdges(Gd, nodeName)
                if flag:
                    for path in pathlist:
                        for i in range(len(path)-1):
                            Gd.edge[path[i]][path[i+1]]['mark'] = 'used'

        sccs = networkx.strongly_connected_component_subgraphs(Gd1)
        for subgraph in sccs:
            for link in subgraph.edges():
                Gd1.edge[link[0]][link[1]]['mark'] = 'used'
                Gd2.edge[link[1]][link[0]]['mark'] = 'used'

        for link in tempG.edges():
            flag0 = tempG.edge[link[0]][link[1]]['label'] == "matching"

            if link[0].endswith("\t+"):
                source = link[0]
                target = link[1]
            else:
                source = link[1]
                target = link[0]

            if flag0:
                flag1 = Gd1[source][target]['mark']=='unused'
                flag2 = Gd2[target][source]['mark']=='unused'
            else:
                flag1 = Gd1[target][source]['mark']=='unused'
                flag2 = Gd2[source][target]['mark']=='unused'

            # for random network
            source = source.strip("\t+")
            target = target.strip("\t-")

            if flag1 and flag2:
                if flag0:
                    self.DG.edge[source][target]['class'] = 'critical'
                else:
                    self.DG.edge[source][target]['class'] = 'redundant'
            else:
                self.DG.edge[source][target]['class'] = 'intermittent'

        pass

    def __BFS_classifyEdges(self,Gd, V0):
        """detect the directed **simple path** which begins at a free node V0

        :V0: @todo
        :returns: return all the simple path begins at V0

        """
        Q=Queue.Queue()
        marked=set()
        siPathlist=list()

        for item in Gd.edge[V0].keys():
            Q.put([V0,item])
            marked.add(item)
	while(not Q.empty()):
	    Vt=Q.get()
	    #if self.node_is_free(Vt[-1]):
            #print Vt[-1]
            #print Gd.edge[Vt[-1]]
            if len(Gd.edge[Vt[-1]])==0:
                # here, should save paths, and wait until Q is empty
		#return True, Vt
                siPathlist.append(Vt)
	    else:
		for Vi in Gd.edge[Vt[-1]].keys():
		    if Vi not in marked:
			marked.add(Vi)
			temp=copy.copy(Vt)
			temp.append(Vi)
			Q.put(temp)

        if len(siPathlist) >0:
            return True, siPathlist
	return False, None

        pass


    def __turnMatchedGp2Gd(self, Gp):
        """trurn Matched Gp to two Gd

	:Gp: @todo
	:returns: @todo

	"""
	Gd1=Gp.to_directed()
        Gd2=Gp.to_directed()

        #look out! Gp is undirected graph, link[0] and link[1] are interchangeable!

        for link in Gp.edges():
            # Here, it needs to determine the source and target, firstly

            if link[0].endswith("+"):
                source=link[0]
                target=link[1]
            else:
                source=link[1]
                target=link[0]

            if Gp.edge[source][target]['label']=='matching':
                Gd1.remove_edge(target,source)
                Gd1.edge[source][target]['mark']='unused'
                Gd2.remove_edge(source,target)
                Gd2.edge[target][source]['mark']='unused'
            else:
                Gd1.remove_edge(source,target)
                Gd1.edge[target][source]['mark']='unused'
                Gd2.remove_edge(target,source)
                Gd2.edge[source][target]['mark']='unused'

        #print "=== Gd1, Gd2 at turnMatchedGp2Gd ==="
        #print Gd1.edges(data=True)
        #print Gd2.edges(data=True)


        return Gd1, Gd2

        pass


    def __BFS_classifyNodes(self, Gd, V0):
        """detect if there is augmenting path from V0

        :Gd: @todo
        :V0: @todo
        :returns: @todo

        """
        Q=Queue.Queue()
        marked=set()

        marked.add(V0)
        for item in Gd.neighbors(V0):
            Q.put([V0,item])
            marked.add(item)
	while(not Q.empty()):
	    Vt=Q.get()
            tempType=Gd.edge[Vt[-1]][Vt[-2]]['label']

	    #if self.node_is_free(Vt[-1]):
            if Gd.node[Vt[-1]]['label']=='free':
		return True
	    else:
		for Vi in Gd.edge[Vt[-1]].keys():
                    # Here needs to add simple path restriction
                    # the previous path label and the following path label, one of them is  matching the other is not
                    nextType=Gd.edge[Vt[-1]][Vi]['label']
		    if (Vi not in marked) and (not tempType==nextType):
			marked.add(Vi)
			temp=copy.copy(Vt)
			temp.append(Vi)
			Q.put(temp)

	return False
        pass

    def __matchNetwork(self, tempG):
        """get a maximum match of Network

        :tempG: temp bipartite graph
	:returns: @None

	"""
	freeNodes=filter(lambda res: res[1]['label']=='free', tempG.nodes(data=True))
        random.shuffle(freeNodes)
	while(len(freeNodes)>0):

	    flag=False
	    indexNode=0
	    augPaths=None

	    while( (not flag) and indexNode<len(freeNodes)):
		flag, augPaths = self.__BFS_MDMS(tempG, freeNodes[indexNode][0])
		if flag:
		    break
		indexNode=indexNode+1

	    # if there is no free node, end loop
	    if( (not flag) and indexNode>=len(freeNodes)):
		break
	    # if there is augPaths but still has free nodes, then,
	    elif( flag and indexNode<len(freeNodes)):
		for i in range(len(augPaths)-1):
		    if tempG.edge[augPaths[i]][augPaths[i+1]]['label']=='free':
			tempG.edge[augPaths[i]][augPaths[i+1]]['label']='matching'
		    else:
			tempG.edge[augPaths[i]][augPaths[i+1]]['label']='free'

                    # refreshing node type
                    if self.__node_is_free(tempG, augPaths[i]):
                        tempG.node[augPaths[i]]['label']='free'
                    else:
                        tempG.node[augPaths[i]]['label']='matched'
                    if self.__node_is_free(tempG, augPaths[i+1]):
                        tempG.node[augPaths[i+1]]['label']='free'
                    else:
                        tempG.node[augPaths[i+1]]['label']='matched'
	    else:
		raise Exception()

	    freeNodes=filter(lambda res: res[1]['label']=='free', tempG.nodes(data=True))
            random.shuffle(freeNodes)
	    #while

        pass

    def __getMDMS(self):
        """
	:returns: @todo

	"""
	for node in self.DG.nodes():

            # Here, driver node should be the nodes in negative partite network which is not connected to matched edge

            matchedEdges=filter(lambda res: res[1]['label']=='matching', tempG.edge["{}\t-".format(node)].iteritems())

            #Here we output one matching
	    if len(matchedEdges)==0:
		self.DG.node[node]['label']="driver"
	    else:
		self.DG.node[node]['label']="matched"


	# return driver nodes
	return filter(lambda res: res[1]['label']=='driver', self.DG.nodes(data=True))

        pass

    def __BFS_MDMS(self, tempG, V0):
        """detect augmenting paths

        :V0: @todo
        :returns: @todo

        """
        Q=Queue.Queue()
	marked=set()
        # look out ! is there any possibility that adding V0 will wipe out the augmenting cycle?
        # Thu Jul 10 09:32:19 CST 2014 add, since there is no odd augmenting cycle, plus the even
        # "augmenting cycle" is not augmenting.
        marked.add(V0)
	for item in tempG.neighbors(V0):
	    Q.put([V0,item]) # return augmenting paths
	    marked.add(item)

	while(not Q.empty()):
	    Vt=Q.get()
            tempType=tempG.edge[Vt[-1]][Vt[-2]]['label']

	    #if self.node_is_free(Vt[-1]):
            if tempG.node[Vt[-1]]['label']=='free':
		return True, Vt
	    else:
		for Vi in tempG.edge[Vt[-1]].keys():
                    # Here needs to add simple path restriction
                    # the previous path label and the following path label, one of them is  matching the other is not
                    nextType=tempG.edge[Vt[-1]][Vi]['label']
		    if (Vi not in marked) and (not tempType==nextType):
			marked.add(Vi)
			temp=copy.copy(Vt)
			temp.append(Vi)
			Q.put(temp)

	return False, None
        pass
    def __node_is_free(self, tempG, V):
        """ the node which is not an endpoint of any matching link is called free node

	:V: @todo
	:returns: @todo

	"""
	for node in tempG.edge[V].keys():
	    if not tempG.edge[node][V]['label']=="free":
		return False
	return True

        pass

    def __sampling(self, f, BiG):
        """Sampling the Maximized Matched Nodes, get the corresponding Minimized Driver Set
        :returns: @todo

        """

        # 0: remove redundant matched node from in set
        tempBiG = self.__removeBiGRedundant(copy.deepcopy(BiG))


        for time in range(f):

            print "finish: {}/{}".format(time,f)
            lastTempBiG = copy.deepcopy(tempBiG)
            # 1: obtain one MMS (denoted by M)
            # MMS, should be the matched in in set.
            # if all the remained nodes in set nodes are free, then there is no need to do sampling
            # because all the drivers are critical
            M = filter(lambda res: res[1]['label']=='matched' and res[0].endswith("\t-"), tempBiG.nodes(data=True))
            if M == []:
                print "no matched nodes except redundant nodes"
                break;
            # 2: randomly pick an element in M (denoted by node i)
            nodei = random.choice(M)
            # here needs to return the corresponding BiG
            # temporary BiG tempBiG, should be a integrate BiG
            # frequency update in this function, enumerateM
            # 3:

            alternativeBiGs = self.__enumerateM(tempBiG, nodei[0])
            # 4:

            if (alternativeBiGs == []) or (alternativeBiGs == None):
                tempBiG = lastTempBiG
                continue
            else:
                tempBiG = random.choice(alternativeBiGs)
                tempBiG = self.__removeBiGRedundant(tempBiG)

    def __enumerateM(self, tempBiG, nodei):
        """@todo: Docstring for enumerateM.

        :tempBiG:
        :nodei: @todo
        :returns: @todo

        """

        alternativeBiGs = []

        hasMore = True
        while hasMore:

            nodej=filter(lambda res: tempBiG.edge[nodei][res]['label']=="matching", tempBiG.neighbors(nodei))[0]
            tempBiG.remove_node(nodei)

            hasMore, augPaths= self.__BFS_sampling(tempBiG, nodej)

            if hasMore:
		for i in range(len(augPaths)-1):
		    if tempBiG.edge[augPaths[i]][augPaths[i+1]]['label']=='free':
			tempBiG.edge[augPaths[i]][augPaths[i+1]]['label']='matching'
		    else:
			tempBiG.edge[augPaths[i]][augPaths[i+1]]['label']='free'

                    # refreshing node type
                    if self.__node_is_free_sampling(tempBiG, augPaths[i]):
                        tempBiG.node[augPaths[i]]['label']='free'
                    else:
                        tempBiG.node[augPaths[i]]['label']='matched'

                    if self.__node_is_free_sampling(tempBiG, augPaths[i+1]):
                        tempBiG.node[augPaths[i+1]]['label']='free'
                    else:
                        tempBiG.node[augPaths[i+1]]['label']='matched'
                self.__updateSampling(alternativeBiGs, copy.deepcopy(tempBiG))
                nodei = augPaths[-1]
        return alternativeBiGs

    def __node_is_free_sampling(self, BiG, V):
        """@todo: Docstring for node_is_free_sampling.

        :BiG: @todo
        :V: @todo
        :returns: @todo

        """

	for node in BiG.edge[V].keys():
	    if not BiG.edge[node][V]['label']=="free":
		return False
	return True

    def __BFS_sampling(self, BiG, V0):
        """BFS

        :BiG: @todo
        :V0: @todo
        :returns: @todo

        """
        Q=Queue.Queue()
        marked=set()

        marked.add(V0)
        for item in BiG.neighbors(V0):
            Q.put([V0,item])
            marked.add(item)
        while(not Q.empty()):
            Vt=Q.get()
            tempType=BiG.edge[Vt[-1]][Vt[-2]]['label']

            #if self.node_is_free(Vt[-1]):
            if BiG.node[Vt[-1]]['label']=='free':
                return True, Vt
            else:
                for Vi in BiG.edge[Vt[-1]].keys():
                    # Here needs to add simple path restriction
                    # the previous path label and the following path label, one of them is  matching the other is not
                    nextType=BiG.edge[Vt[-1]][Vi]['label']
                    if (Vi not in marked) and (not tempType==nextType):
                        marked.add(Vi)
                        temp=copy.copy(Vt)
                        temp.append(Vi)
                        Q.put(temp)

        return False, None


    def __removeBiGRedundant(self, BiG):
        """remove the critical node from  bipartite networkx
        :returns: @todo

        """

        #
        redundantNodes = self.__getNodesByClass(["redundant"])
        for nd in redundantNodes:
            BiG.remove_node("{}\t-".format(nd))

        return BiG

    def __updateSampling(self, alternativeBiGs, tempBiG):
        """@todo: Docstring for updateSampling.

        :alternativeMs: @todo
        :alternativeBiGs: @todo
        :tempBiG: @todo
        :returns: @todo

        """

        completeBiG = self.__getCompleteBiG(tempBiG)
        alternativeBiGs.append(completeBiG)

        # here, GcsP probably has no some nodes
        # check the integrity of GcsP
        for node in self.DG.nodes():
            matchedEdges=filter(lambda res: res[1]['label']=='matching', completeBiG.edge["{}\t-".format(node)].iteritems())
	    if len(matchedEdges)==0:
                self.DG.node[node]['frequency'] = self.DG.node[node].get('frequency', 0) +1

        matchingLinks = [(s,t) for (s,t,a) in completeBiG.edges(data=True) if a['label']=='matching']
        for ml in matchingLinks:
            if ml[0].endswith("\t+"):
                sourceNode = ml[0].strip("\t+")
                targetNode = ml[1].strip("\t-")
            else:
                sourceNode = ml[1].strip("\t+")
                targetNode = ml[0].strip("\t-")
            self.DG[sourceNode][targetNode]['frequency'] = self.DG[sourceNode][targetNode].get('frequency', 0) +1

    def __getNodesByClass(self, types):
        """get node set by class

        :types: @todo
        :returns: @todo

        """

        return [ n for (n,a) in self.DG.nodes(data=True) if a['class'] in types ]

    def __getCompleteBiG(self, tempBiG):
        """@todo: Docstring for getCompleteBiG.

        :tempBiG: @todo
        :returns: @todo

        """

        # self. get nodes by class
        redundantNodes = self.__getNodesByClass(["redundant"])
        completeBiG = copy.deepcopy(tempBiG)

        posNodes = [ n for n in completeBiG.nodes() if n.endswith("\t+") ]
        for pn in posNodes:
            counterpart = "{}\t-".format(pn.strip("\t+"))
            if counterpart not in completeBiG.nodes():
                completeBiG.add_node(counterpart)
                # here to distinguish between redundant nodes and the others
                if pn.strip("\t+") in redundantNodes:
                    completeBiG.node[counterpart]['label'] = 'matched'
                else:
                    completeBiG.node[counterpart]['label'] = 'free'
                # self.BIG
                for cn in self.bipartite.neighbors(counterpart):
                    completeBiG.add_edge(counterpart, cn)
                    # needs to verify current link is the original matching link
                    if pn.strip("\t+") in redundantNodes:
                        completeBiG.edge[counterpart][cn]['label'] = self.bipartite.edge[counterpart][cn]['label']
                    else:
                        completeBiG.edge[counterpart][cn]['label'] = 'free'

        return completeBiG

    def __printNodesAttri(self, attributes):
        """@todo: Docstring for printNodes.
        :returns: @todo

        """

        for (n, a) in self.DG.nodes(data = True):
            astring = ""
            for att in attributes:
                if att in a.keys():
                    astring = "{0}\t{1}".format(astring, a[att])
            print "{0}\t{1}".format(n, astring)

    def __exportNFNetwork_Cytoscape(self, nodeAttributeFilePath):
        """@todo: Docstring for exportNFNetwork_Cytoscape.

        :nodeAttributeFilePath: @todo
        :returns: @todo

        """

        with open(nodeAttributeFilePath,'w') as outFile:
            for (n,a) in self.DG.nodes(data=True):
                if 'frequency' in a.keys():
                    outFile.write("{0}\t{1}\t{2}\n".format(n,a['class'],a['frequency']))
                else:
                    outFile.write("{0}\t{1}\t{2}\n".format(n,a['class'],0))


    def Enum_Maximum_Matching(self, GcsP):
        """main function of enumerate all maximum matching in G'cs(P)

        :G: @todo
        :returns: @todo

        """
        #step1. find a maximal matching M of G, and output M
        self.__matchNetwork(GcsP)
        #self.outPutMatching(GcsP)

        G = self.__getDGM(GcsP)
        #step2: trim unnecessary edges from G by a strongly connected component decomposition algorithm with D(G,M)
        self.__trim(G)

        #step3: call iteration to enumerate
        self.__Enum_Maximum_Matchings_Iter(GcsP, G)

    def __Enum_Maximum_Matchings_Iter(self, GcsP, G):
        """iteration of enumerate perfect matchings in Gcs(P)

        :G: @todo
        :M: @todo
        :returns: @todo

        """
        #step1: if G has no edge, stop
        if GcsP.number_of_edges() == 0:
            return

        #step2: if D(G, M) contains no cycle, Go to step 8
        if not G.number_of_edges() == 0:
            #step3: Choose an edge e both in current matching and cycle
            e = [(s,t) for (s,t,a) in G.edges(data=True) if a['label']=='matching'][0]
            #step4: Find a cycle containing e by a depth-first-search algorithm
            hasCycle, Cycle = self.__DFS_EnumerateMaximumMatching(G, e)
            #step5: Exchange edges along the cycle and output the obtained maximum matching M'
            GcsP_new = self.__step5(GcsP, Cycle)
            #step6: Enumerate all maximum matchings including e by Enum_Maximum_Matchings_Iter with G+(e)
            # M and trimmed D(G+, M/e)
            self.__step6(GcsP, e)
            #step7: Enumerate all maximum matchings including e by Enum_Maximum_Matchings_Iter with G-(e)
            # M and trimmed D(G-, M/e)
            self.__step7(GcsP_new, e)

            return
            pass
        #step 8: Find a feasible path with length 2 and generate a new maximum matching M'.
        #let e be the edge of the path not included in M
        flag, e, GcsP_new = self.__step8(GcsP)
        #print "e:",e
        if flag:
            self.__step9(GcsP_new, e)
            self.__step10(GcsP, e)

        pass

    def __updateNodeLabel(self, GcsP):
        """update node label timely, while call Enum_Maximum_Matching recursively.

        :GcsP: @todo
        :returns: @todo

        """
        for nd in GcsP.nodes():
            if self.__node_is_free(GcsP, nd):
                GcsP.node[nd]['label'] = 'free'
            else:
                GcsP.node[nd]['label'] = 'matched'

    def __step10(self, GcsP, e):

        #GcsP is new matched Graph
        GcsP_N = copy.deepcopy(GcsP)
        GcsP_N.remove_edge(*e)
        #GcsP_N with old match
        self.__updateNodeLabel(GcsP_N)
        self.__Enum_Maximum_Matchings_Iter(GcsP_N, networkx.DiGraph())

    def __step9(self, GcsP, e):
        """@todo: Docstring for step9.

        :Gcsp: @todo
        :e: @todo
        :returns: @todo

        """
        GcsP_P = copy.deepcopy(GcsP)
        GcsP_P.remove_nodes_from([e[0], e[1]])
        self.__updateNodeLabel(GcsP_P)
        #GcsP_P with new match
        self.__Enum_Maximum_Matchings_Iter(GcsP_P, networkx.DiGraph())

        pass

    def __step8(self, GcsP):
        """step8

        :GcsP: @todo
        :returns: @todo

        """
        # uncovered nodes is unmatched nodes with edge incident to it
        #nodeCoveredSet = min_weighted_vertex_cover(GcsP)
        #nodeUncoverSet = set(GcsP.nodes()) - nodeCoveredSet
        GcsP_new = copy.deepcopy(GcsP)

	freeNodes=filter(lambda res: res[1]['label']=='free', GcsP_new.nodes(data=True))
        # node label is not update timely, then, this is a potential bug
        #print GcsP_new.nodes(data = True), GcsP_new.edges(data = True)


        for node, attr in freeNodes:
            if len(GcsP_new.neighbors(node)) == 0:
                continue
            else:
                # find the feasible path with length 2
                flag, path2 = self.__findFeasiblePath2(GcsP_new, node)
                if not flag:
                    break

                v0 = path2[0]
                v1 = path2[1]
                v2 = path2[2]
                if GcsP_new.edge[v0][v1]['label'] == 'matching':
                    GcsP_new.edge[v0][v1]['label'] = 'free'
                else:
                    GcsP_new.edge[v0][v1]['label'] = 'matching'
                    e = (v0, v1)
                if GcsP_new.edge[v1][v2]['label'] == 'matching':
                    GcsP_new.edge[v1][v2]['label'] = 'free'
                else:
                    e = (v1, v2)
                    GcsP_new.edge[v1][v2]['label'] = 'matching'
                self.__updateNodeLabel(GcsP_new)
                self.__outPutMatching(GcsP_new)
                return True, e, GcsP_new
        return False, None, None

    def __findFeasiblePath2(self, GcsP, V0):
        """find the feasible path with length2

        :GcsP: @todo
        :node: @todo
        :returns: @todo

        """
        Q=Queue.Queue()
        marked=set()

        for item in GcsP.edge[V0].keys():
            Q.put([V0,item])
            marked.add(item)
	while(not Q.empty()):
	    Vt=Q.get()
            tempType=GcsP.edge[Vt[-1]][Vt[-2]]['label']
            if len(GcsP.edge[Vt[-1]])==0:
                continue
            if len(Vt) == 3:
                return True, Vt
	    else:
		for Vi in GcsP.edge[Vt[-1]].keys():
                    nextType=GcsP.edge[Vt[-1]][Vi]['label']
		    if (Vi not in marked) and (not tempType==nextType):
			marked.add(Vi)
			temp=copy.copy(Vt)
			temp.append(Vi)
			Q.put(temp)

	return False, None

    def __step7(self, GcsP, e):

        GcsP_N = copy.deepcopy(GcsP)
        GcsP_N.remove_edge(*e)
        self.__updateNodeLabel(GcsP_N)
        Gd_N = self.__getDGM(GcsP_N)
        Gd_N = self.__trim(Gd_N)
        self.__Enum_Maximum_Matchings_Iter(GcsP_N, Gd_N)

    def __step6(self, GcsP, e):
        """step6
        GcsP+ is obtained by deleting the vertexs of edges

        :GcsP: @todo
        :G: @todo
        :returns: @todo

        """
        GcsP_P = copy.deepcopy(GcsP)
        GcsP_P.remove_nodes_from([e[0], e[1]])
        self.__updateNodeLabel(GcsP_P)
        Gd_P = self.__getDGM(GcsP_P)
        Gd_P = self.__trim(Gd_P)
        self.__Enum_Maximum_Matchings_Iter(GcsP_P, Gd_P)

    def __step5(self, GcsP, Cycle):
        """exchange edges along the cycle and outPut the obtained maximum matching M'

        :GcsP: @todo
        :Cycle: @todo
        :returns: @todo

        """
        GcsP_new = copy.deepcopy(GcsP)
        for i in range(len(Cycle)-1):
            if GcsP_new.edge[Cycle[i]][Cycle[i+1]]['label'] == 'matching':
                GcsP_new.edge[Cycle[i]][Cycle[i+1]]['label'] = 'free'
            else:
                GcsP_new.edge[Cycle[i]][Cycle[i+1]]['label'] = 'matching'

        self.__updateNodeLabel(GcsP_new)
        self.__outPutMatching(GcsP_new)
        return GcsP_new

    def __DFS_EnumerateMaximumMatching(self, G, e):
        """Find a cycle containing e by a depth first search algorithm

        :G: trimed bipartite graph
        :e: an edge both in M and cycle
        :returns: @todo

        """

        stack = []
        marked = set()

        V0 = e[0]
        stack.append([e[0],e[1]])
        marked.add(e[1])

        while len(stack) > 0:
	    Vt = stack.pop()

            if Vt[-1] == V0:
                # caution: if node V0 has a self pointed
                return True, Vt
	    else:
		for Vi in G.edge[Vt[-1]].keys():
		    if Vi not in marked:
			marked.add(Vi)
			temp=copy.deepcopy(Vt)
			temp.append(Vi)
			stack.append(temp)

	return False, None




    def __trim(self, G):
        """trim unnecessary edges which are included in no cycle before generating a subproblem
        Cycle can be found by strongly connected component decomposition

        :G: @todo
        :returns: @todo

        """
        sccs = networkx.strongly_connected_component_subgraphs(G)

        edgesRemain = set()
        for subgraph in sccs:
            edgesRemain = set.union(edgesRemain, set(subgraph.edges()))

        for link in G.edges():
            if (link[0], link[1]) not in edgesRemain:
                G.remove_edge(link[0], link[1])

        return G
    def __getDGM(self, G):
        """transform bipartite graph GcsP (matched) to directed bipartite graph
        Its vertex set is V, and its arc set is given by orienting edges of M
        from V1 to V2, and the other edges of G in the opposite direction

        :G: @todo
        :returns: @todo

        """
        Gd1 = G.to_directed()
        #look out! Gp is undirected graph, link[0] and link[1] are interchangeable!

        for link in G.edges():
            # Here, it needs to determine the source and target, firstly

            if link[0].endswith("+"):
                source=link[0]
                target=link[1]
            else:
                source=link[1]
                target=link[0]

            if G.edge[source][target]['label']=='matching':
                Gd1.remove_edge(target,source)
            else:
                Gd1.remove_edge(source,target)

        return Gd1

