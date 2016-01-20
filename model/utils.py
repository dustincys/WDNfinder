#!/usr/bin/env python
# encoding: utf-8
'''
# =============================================================================
#      FileName: utils.py
#          Desc:
#        Author: Chu Yanshuo
#         Email: chu@yanshuo.name
#      HomePage: http://yanshuo.name
#       Version: 0.0.1
#    LastChange: 2015-12-22 12:54:08
#       History:
# =============================================================================
'''

import networkx

def fromFile(inputFilePath="/media/d/data/driver/sourceData.txt", directed=True, isWeighted = False):
    """ read network from file
    :usage:
    :inputFilePath: source data path, two column data,
                    "source  target"
    :returns: networkx object
    """

    if directed:
        DG=networkx.DiGraph()
    else:
        DG=networkx.Graph()

    with open(inputFilePath) as inFile:
        for line in inFile:
            line=line.strip()
            if line=="":
                continue
            listLine=line.split("\t")

	    source=listLine[0].strip()
	    target=listLine[1].strip()

            DG.add_edge(source,target)

            if isWeighted:
                DG[source][target]['weight'] = float(listLine[2])

            pass
    return DG
    pass

def toBipartite(digraph, isWeighted = True):
    """copy from a weighted digraph

    :digraph: @todo
    :returns: @todo

    """

    bipartite = networkx.Graph()

    for n in digraph.nodes():
        bipartite.add_node("{}\t+".format(n), label='free')
        bipartite.add_node("{}\t-".format(n), label='free')
    for (s,t,a) in digraph.edges(data = True):
        bipartite.add_edge("{}\t+".format(s), "{}\t-".format(t), label="free")
        if isWeighted:
            bipartite["{}\t+".format(s)]["{}\t-".format(t)]['weight'] = a['weight']

    return bipartite

def randomNetwork(nodesNum=5):
    """
    :returns: @todo

    """
    edge_set=set()
    rn=networkx.scale_free_graph(nodesNum)
    for (s,t,a) in rn.edges(data=True):
        if s==t:
            rn.remove_edge(s,t)
            continue
        if (s,t) not in edge_set:
            edge_set.add((s,t))
        else:
            rn.remove_edge(s,t)
    rn2=networkx.DiGraph()
    for (s,t) in rn.edges():
        rn2.add_edge(str(s), str(t))

    return rn2

def exportNodeAttribute(directedGraph, nodeAttributeFilePath):
    """@todo: Docstring for exportNodeAttribute.

    :nodeAttributeFilePath: @todo
    :returns: @todo

    """

    with open(nodeAttributeFilePath, 'w') as outFile:
        for (n, a) in directedGraph.nodes(data = True):
            if 'frequency' in a.keys():
                outFile.write("{0}\t{1}\t{2}\n".format(n,a['class'],a['frequency']))
            else:
                outFile.write("{0}\t{1}\t{2}\n".format(n,a['class'],0))

def exportEdgeAttribute(directedGraph, edgeAttributeFilePath):
    """TODO: Docstring for exportEdgeAttribute.

    :directedGraph: TODO
    :edgeAttributeFilePath: TODO
    :returns: TODO

    """

    with open(edgeAttributeFilePath, 'w') as outFile:
        for (s, t, a) in directedGraph.edges(data = True):
            #print a.keys()
            if 'frequency' in a.keys():
                if 'class' in a.keys():
                    outFile.write("{0}\t{1}\t{2}\t{3}\n".format(s, t, a['class'], a['frequency']))
                else:
                    outFile.write("{0}\t{1}\t{2}\t{3}\n".format(s, t, "redundant", a['frequency']))
            else:
                if 'class' in a.keys():
                    outFile.write("{0}\t{1}\t{2}\t{3}\n".format(s, t, a['class'], 0))
                else:
                    outFile.write("{0}\t{1}\t{2}\t{3}\n".format(s, t, "redundant", 0))

