#!/usr/bin/env python
# Tai Sakuma <tai.sakuma@cern.ch>
import os
import argparse
from AlphaTwirl import EventBuilder, CombineIntoPandasDataFrame, WritePandasDataFrameToFile
from AlphaTwirl.HeppyResult import HeppyResult
from AlphaTwirl.Counter import Counts, GenericKeyComposer, CounterBuilder
from AlphaTwirl.Binning import RoundLog, Echo
from AlphaTwirl.EventReader import Collector
from AlphaTwirl.ProgressBar import ProgressBar, ProgressReport, ProgressMonitor

##__________________________________________________________________||
parser = argparse.ArgumentParser()
parser.add_argument('-i', '--heppydir', default = '/Users/sakuma/work/cms/c150130_RA1_data/c150130_01_PHYS14/201525_SingleMu', help = "Heppy results dir")
parser.add_argument('-o', '--outdir', default = 'tmp')
parser.add_argument("-n", "--nevents", default = -1, type = int, help = "maximum number of events to process for each component")
args = parser.parse_args()

analyzerName = 'treeProducerSusyAlphaT'
fileName = 'tree.root'
treeName = 'tree'

outPath1 = os.path.join(args.outdir, 'tbl_met.txt')
binning1 = RoundLog(0.1, 0)
keyComposer1 = GenericKeyComposer(('met_pt', ), (binning1, ))
counterBuilder1 = CounterBuilder(Counts, ('met', ), keyComposer1)
resultsCombinationMethod1 = CombineIntoPandasDataFrame()
deliveryMethod1 = WritePandasDataFrameToFile(outPath1)
collector1 = Collector(resultsCombinationMethod1, deliveryMethod1)

outPath2 = os.path.join(args.outdir, 'tbl_jetpt.txt')
binning2 = RoundLog(0.1, 0)
keyComposer2 = GenericKeyComposer(('jet_pt', ), (binning2, ), (0, ))
counterBuilder2 = CounterBuilder(Counts, ('jet_pt', ), keyComposer2)
resultsCombinationMethod2 = CombineIntoPandasDataFrame()
deliveryMethod2 = WritePandasDataFrameToFile(outPath2)
collector2 = Collector(resultsCombinationMethod2, deliveryMethod2)

outPath3 = os.path.join(args.outdir, 'tbl_njets_nbjets.txt')
binning31 = Echo()
binning32 = Echo()
keyComposer3 = GenericKeyComposer(('nJet40', 'nBJet40'), (binning31, binning32))
counterBuilder3 = CounterBuilder(Counts, ('njets', 'nbjets'), keyComposer3)
resultsCombinationMethod3 = CombineIntoPandasDataFrame()
deliveryMethod3 = WritePandasDataFrameToFile(outPath3)
collector3 = Collector(resultsCombinationMethod3, deliveryMethod3)

eventBuilder = EventBuilder(analyzerName, fileName, treeName, args.nevents)

class AllEvents(object):
    def __call__(self, event): return True

eventSelection = AllEvents()

progressBar = ProgressBar()
progressMonitor = ProgressMonitor(progressBar)
progressReporter = progressMonitor.createReporter()

heppyResult = HeppyResult(args.heppydir)
for component in heppyResult.components():

    counter1 = counterBuilder1()
    collector1.addReader(component.name, counter1)

    counter2 = counterBuilder2()
    collector2.addReader(component.name, counter2)

    counter3 = counterBuilder3()
    collector3.addReader(component.name, counter3)

    events = eventBuilder.build(component)
    for event in events:

        report = ProgressReport(component.name, event.iEvent + 1, event.nEvents)
        progressReporter.report(report)

        if not eventSelection(event): continue

        counter1.event(event)
        counter2.event(event)
        counter3.event(event)

collector1.collect()
collector2.collect()
collector3.collect()

##__________________________________________________________________||
