#!/usr/bin/env python
# Tai Sakuma <tai.sakuma@cern.ch>
import ROOT
import os
import argparse

##__________________________________________________________________||
parser = argparse.ArgumentParser()
parser.add_argument('-i', '--heppydir', default = '/Users/sakuma/work/cms/c150130_RA1_data/c150130_01_PHYS14/201525_SingleMu', help = "Heppy results dir")
parser.add_argument('-o', '--outdir', default = 'tmp')
parser.add_argument("-n", "--nevents", default = -1, type = int, help = "maximum number of events to process for each component")
args = parser.parse_args()

analyzerName = 'treeProducerSusyAlphaT'
fileName = 'tree.root'
treeName = 'tree'
outPath = os.path.join(args.outdir, 'tbl_met.txt')

outFile = open(outPath, 'w')
print >>outFile, "{:>22s} {:>12s} {:>6s}".format("component", "met", "n")

for component in os.listdir(args.heppydir):
    if component in ('Chunks', 'failed'): continue
    componentPath = os.path.join(args.heppydir, component)
    if not os.path.isdir(componentPath): continue
    analyzerPath = os.path.join(componentPath, analyzerName)
    inputPath = os.path.join(analyzerPath, fileName)

    inputFile = ROOT.TFile.Open(inputPath)
    tree = inputFile.Get(treeName)

    boundaries = [10**(i*0.1) for i in range(-10, 36)]
    counts = { }

    nevents = min(tree.GetEntries(), args.nevents) if args.nevents >= 0 else tree.GetEntries()
    for i in xrange(nevents):
        if tree.GetEntry(i) <= 0: break

        met = tree.met_pt
        met_bin = max([b for b in boundaries if b < met])

        if not met_bin in counts: counts[met_bin] = 0
        counts[met_bin] += 1

    keys = counts.keys()
    keys.sort()
    for k in  keys:
        print >>outFile, "{:>22s} {:12.6f} {:6d}".format(component, k, counts[k])

##__________________________________________________________________||
