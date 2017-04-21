# Tai Sakuma <tai.sakuma@cern.ch>
import os

import ROOT

from .EventBuilderConfig import EventBuilderConfig
from .load_delphes import load_delphes

##__________________________________________________________________||
class EventBuilderConfigMaker(object):
    def __init__(self):
        self.treeName = 'Delphes'

    def create_config_for(self, dataset, files, start, length):
        config = EventBuilderConfig(
            inputPaths = files,
            treeName = self.treeName,
            maxEvents = length,
            start = start,
            dataset = dataset, # for scribblers
            name = dataset.name # for the progress report writer
        )
        return config

    def file_list_in(self, dataset, maxFiles):
        if maxFiles < 0:
            return dataset.files
        return dataset.files[:min(maxFiles, len(dataset.files))]

    def nevents_in_file(self, path):
        load_delphes()
        file = ROOT.TFile.Open(path)
        tree = file.Get(self.treeName)
        return tree.GetEntries() # GetEntries() is slow. call only as
                                 # many times as necessary

##__________________________________________________________________||
