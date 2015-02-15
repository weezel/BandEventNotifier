#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pylast

import os
import pickle
import sys

API_KEY = ""
API_SECRET = ""

def readAPIkeys(fname):
    global API_KEY, API_SECRET
    data = []

    with open(fname, "r") as f:
        for line in f:
            data.append(line.replace("\n", ""))
    if len(data) < 2:
        return False

    API_KEY, API_SECRET = data[0], data[1]
    return True

def previousLibraryFetch(fname):
    pass

def getAllBandsFromLibrary(username):
    network = pylast.get_lastfm_network(API_KEY, API_SECRET)
    user = pylast.User(username, network)
    library = pylast.Library(username, network)

    return [artist for artist in library.get_artists(limit = None)]

def calculatePopularity(allbands, thisband):
    totalplaycount = sum([artist.playcount for artist in allbands])
    return float(thisband.playcount) / totalplaycount * 1000

if __name__ == '__main__':
    storaname = "allbands.dump"
    allbands = []

    if readAPIkeys("APIKEYS") == False:
        sys.exit("Couldn't find file for API keys")

    if os.path.isfile(storaname):
        # TODO check whether the file timestamp is new enough
        allbands = pickle.load(open(storaname, "rb"))
    else:
        allbands = getAllBandsFromLibrary("weezel_ding")
        pickle.dump(allbands, open(storaname, "wb"))

    for i, artist in enumerate(allbands[0 : 300]):
        print "%2d %-40s %.2f%% %-5d" % (i + 1, artist.item,
                calculatePopularity(allbands, artist), artist.playcount)

