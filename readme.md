# WDNfinder: a method for minimum driver node detection 

## Requires

- python2.7
- Networkx (it seems nest networkx package no longer support iter)

## Usage

	usage: WDNfinder [-h] {weightedNodeAnalysis,unweightedNodeAnalysis,unweightedMDSEnumerate,weightedMDSEnumerate}                 ...

### Minimum driver node set (MDS) enumeration

	python2.7 WDNfinder.py unweightedMDSEnumerate ./data/test/sourceData.txt

### Maximum Weight Minimum driver node set (MWMDS) enumeration

	python2.7 WDNfinder.py weightedMDSEnumerate ./data/test/sourceData.txt

### MDS based node classification and sampling

	python2.7 WDNfinder.py unweightedNodeAnalysis ./data/test/sourceData.txt sourceData_unweighted

### MWMDS based node classification and sampling

	python2.7 WDNfinder.py weightedNodeAnalysis ./data/test/sourceData.txt sourceData_weighted

## Data

### human cancer signaling network (HCSN)
	./data/HCSN
### p53-mediate DNA damage response network
	./data/p53

