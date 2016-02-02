#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
# =============================================================================
#      FileName: weightedNetworkAnalysis.py
#          Desc:
#        Author: Chu Yanshuo
#         Email: chu@yanshuo.name
#      HomePage: http://yanshuo.name
#       Version: 0.0.1
#    LastChange: 2015-12-23 19:28:32
#       History:
# =============================================================================
'''
from model.utils import *
from model.gcsp import *
from model.structuralcontrol import *

import pickle

import argparse

def weightedNetworkAnalysis(args):

    directedGraph = fromFile(args.network, isWeighted = True)
    bipartiteGraph =toBipartite(directedGraph)

    getGCSP = GCSP(directedGraph, bipartiteGraph)
    gcsp = getGCSP.constructGcsP()

    structuralcontrol = StructuralControl(directedGraph, gcsp)
    if args.sampling_times == -1:
        structuralcontrol.samplingWeight(50*gcsp.number_of_nodes())
    else:
        structuralcontrol.samplingWeight(args.sampling_times)

    exportNodeAttribute(directedGraph, args.prefix+ ".node")

def unweightedNetworkAnalysis(args):

    directedGraph = fromFile(args.network, isWeighted = False)
    bipartiteGraph =toBipartite(directedGraph, isWeighted = False)

    structuralcontrol = StructuralControl(directedGraph, bipartiteGraph)
    if args.sampling_times == -1:
        structuralcontrol.samplingWeight(100*directedGraph.number_of_nodes())
    else:
        structuralcontrol.samplingWeight(args.sampling_times)

    exportNodeAttribute(directedGraph, args.prefix+ ".node")

def weightedEnumerateMatching(args):

    directedGraph = fromFile(args.network, isWeighted = True)
    bipartiteGraph =toBipartite(directedGraph)

    getGCSP = GCSP(directedGraph, bipartiteGraph)
    gcsp = getGCSP.constructGcsP()

    structuralcontrol = StructuralControl(directedGraph, gcsp)
    structuralcontrol.Enum_Maximum_Matching()

def unweightedEnumerateMatching(args):

    directedGraph = fromFile(args.network, isWeighted = True)
    bipartiteGraph =toBipartite(directedGraph)

    structuralcontrol = StructuralControl(directedGraph, bipartiteGraph)
    structuralcontrol.Enum_Maximum_Matching()

parser = argparse.ArgumentParser(prog='WDNfinder')

subparsers = parser.add_subparsers()

#===============================================================================
# Add weightedAnalysis sub-command
#===============================================================================
weightedAnalysis = subparsers.add_parser('weightedNodeAnalysis', help='''Weighted network analysis''')
weightedAnalysis.add_argument('network', help='''network file, format: source\ttarget\weight''')
weightedAnalysis.add_argument('prefix', help='''prefix of output''')
weightedAnalysis.add_argument('--sampling_times', default=-1, type=int, help='''Sampling times for weighted network. Default is 50* number of nodes in gcsp.''')
weightedAnalysis.set_defaults(func=weightedNetworkAnalysis)

#===============================================================================
# Add unweightedAnalysis sub-command
#===============================================================================
unweightedAnalysis = subparsers.add_parser('unweightedNodeAnalysis', help='''Weighted network analysis''')
unweightedAnalysis.add_argument('network', help='''network file, format: source\ttarget\weight''')
unweightedAnalysis.add_argument('prefix', help='''prefix of output''')
unweightedAnalysis.add_argument('--sampling_times', default=-1, type=int, help='''Sampling times for weighted network. Default is 50* number of nodes in gcsp.''')
unweightedAnalysis.set_defaults(func=unweightedNetworkAnalysis)

#===============================================================================
# Add unweightedEnumerate sub-command
#===============================================================================
unweightedEnumerate = subparsers.add_parser('unweightedMDSEnumerate', help='''Weighted network analysis''')
unweightedEnumerate.add_argument('network', help='''network file, format: source\ttarget\weight''')
unweightedEnumerate.add_argument('prefix', help='''prefix of output''')
unweightedEnumerate.set_defaults(func=unweightedEnumerateMatching)


#===============================================================================
# Add weightedEnumerate sub-command
#===============================================================================
weightedEnumerate = subparsers.add_parser('weightedMDSEnumerate', help='''Weighted network analysis''')
weightedEnumerate.add_argument('network', help='''network file, format: source\ttarget\weight''')
weightedEnumerate.add_argument('prefix', help='''prefix of output''')
weightedEnumerate.set_defaults(func=weightedEnumerateMatching)

args = parser.parse_args()
args.func(args)
#def main():
#    folderPath = "data/HCSN/"
#    targetFiles = ["sourceData_W_BP_Lin.txt"]
#    for targetFile in targetFiles:
#        dataPath = folderPath + targetFile
#        outputFilePath = dataPath + ".result.weighted"
#        weightedAnalysis(dataPath, outputFilePath)
#        outputFilePath = dataPath + ".result.notweighted"
#        notWeightedAnalysis(dataPath, outputFilePath)
#
#if __name__ == "__main__":
#    main()
