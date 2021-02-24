#!/usr/bin/env python
"""
Create a .csv file to feed to the gmdSimIoc caproto IOC. Reads 100 
un-damaged events from the specified detector and puts the data into the
specified file.

Arguments
---------

experiment : str
    The experiment to pull (X)GMD data from, e.g. tmox43218

run : int
    Run number to pull data from.

detector : str
    The detector name to pull (X)GMD data from, e.g. xgmdstr0 (XGMD electron
    stream 1).

file_name : str
    The filename to write the .csv data to. 
"""

from psana import DataSource

import sys
import csv

args = sys.argv

ds = DataSource(exp=args[1], run=int(args[2]))
run = next(ds.runs())
det = run.Detector(args[3])
raw_streams = []
ngood = 0
for evt in run.events():
    stream = det.raw.value(evt)
    if stream is not None:
        raw_streams.append(stream)
        ngood += 1
    if ngood >= 100: break

with open(args[4], 'w', newline='') as csvfile:
    writer = csv.writer(csvfile, delimiter=',')
    for raw in raw_streams:
        writer.writerow(raw)
