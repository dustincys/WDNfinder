'''
# =============================================================================
#      FileName: gcsp.py
#          Desc:
#        Author: Chu Yanshuo
#         Email: chu@yanshuo.name
#      HomePage: http://yanshuo.name
#       Version: 0.0.1
#    LastChange: 2015-12-22 13:08:30
#       History:
# =============================================================================
'''
import kuhnMunkres
import copy
import networkx
import datetime

class GCSP:

    def __init__(self, directedGraph, bipartite):
        """TODO: Docstring for __init__.

        :bipartite: TODO
        :returns: TODO

        """
        self.DG = directedGraph
        self.bipartite = bipartite
        self.DGNodes = self.DG.nodes()
        self.DGEdges = self.DG.edges()
        pass

    def constructGcsP(self):
        """Construct the subgraph Gcs(P)=(U \cup V, Ees)
        According to paper "optimum matchings in weighted bipartite graphs"
        GcsP is obtained by removing the edges uv of G such that w(uv) -\pi(u)-p(v) != 0

        :returns: subgraph Gcs(P), the auxiliary subgraph, bipartite

        """
        BiG_re = copy.deepcopy(self.bipartite)
        weightMatrix = self.__getWM()
        Mu, Mv, val, lu, lv = kuhnMunkres.maxWeightMatching(weightMatrix)
        #print "lu:", lu
        #print "lv", lv

        print "begin [[constructGcsP_getResult"
        time1 = datetime.datetime.now()
        [[self.__constructGcsP_getResult(j, i, BiG_re, weightMatrix, lu, lv) for i in range(len(self.DGNodes))] for j in range(len(self.DGNodes))]
        time2 = datetime.datetime.now()
        print "time elapsed: {}".format(time2 - time1)
        print "finish [[constructGcsP_getResult"

        return BiG_re

    def __constructGcsP_getResult(self, i, j, BiG_re, weightMatrix, lu, lv):

        nodei = self.DGNodes[i]
        nodej = self.DGNodes[j]
        if lu[i] + lv[j] != weightMatrix[i][j]:
            # caution: BiG_re is undirected graph, possition of nodei and nodej are exchangeable
            # catch exception and ignore it
            try:
                BiG_re.remove_edge("{}\t+".format(nodei), "{}\t-".format(nodej))
            except networkx.NetworkXError:
                pass
        pass

    def __getWM(self):
        """get the weight matrix for kuhnMunkres mathod
        :returns: @todo

        """
        dummyW = -1
        for s, t, a in self.DG.edges(data = True):
            # multipy to ensure integral
            dummyW = dummyW - int(a['weight']*1000)

        print "begin getWM"
        time1 = datetime.datetime.now()
        matrix = [[self.__getWM_result(j, i, dummyW) for i in range(len(self.DGNodes))] for j in range(len(self.DGNodes))]
        time2 = datetime.datetime.now()
        print "time elapsed: {}".format(time2 - time1)
        print "finished getWM"

        return matrix

    def __getWM_result(self, i, j, dummyW):

        nodei = self.DGNodes[i]
        nodej = self.DGNodes[j]
        if (nodei, nodej) not in self.DGEdges:
            # assign -max(all nodes weight) to dummy weight
            return dummyW
        else:
            return int(self.DG[nodei][nodej]['weight']*1000)

