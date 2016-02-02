# WDNfinder: a method for minimum driver node detection 

## Requires

- python2.7
- Networkx

## Usage

	usage: WDNfinder [-h] {weightedNodeAnalysis,unweightedNodeAnalysis,unweightedMDSEnumerate,weightedMDSEnumerate}                 ...

### Minimum driver node set (MDS) enumeration

	./WDNfinder unweightedMDSEnumerate ./data/test/sourceData.txt

### Maximum Weight Minimum driver node set (MWMDS) enumeration

	./WDNfinder weightedMDSEnumerate ./data/test/sourceData.txt

### MDS based node classification and sampling

	./WDNfinder unweightedNodeAnalysis ./data/test/sourceData.txt sourceData_unweighted

### MWMDS based node classification and sampling

	./WDNfinder weightedNodeAnalysis ./data/test/sourceData.txt sourceData_weighted

## Data

### human cancer signaling network (HCSN)
	./data/HCSN
### p53-mediate DNA damage response network
	./data/p53

