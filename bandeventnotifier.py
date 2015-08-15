#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import sys
import threading
from Queue import Queue

import dbengine
from plugin_handler import load_venue_plugins
import lastfmfetch

MAX_THREADS = 6


class Fetcher(threading.Thread):
    def __init__(self, q, dbobj=None):
        threading.Thread.__init__(self)
        self.fetchqueue = q
        self.dbeng = None

        self.__dbInit(dbobj)

    def __dbInit(self, dbobj):
        if self.dbeng == None:
            self.dbeng = dbobj

    def run(self):
        while True:
            venue = self.fetchqueue.get()
            self.fetchAndParse(venue)
            print "[-] Fetching parsing '%s'" % (venue.name)
            self.fetchqueue.task_done()
            # TODO Implement callback to inform completed venues
            #print "[+] Fetching '%s' completed" % (venue.name)

    def fetchAndParse(self, venue):
        retries = 3
        r = requests.get(venue.url)

        if r.status_code is not 200:
            for retry in range(0, retries):
                print "Couldn't connect %s, retrying %d/%d..." % \
                        (venue.url, retry + 1, retries)
                r = requests.get(venue.url)

                if r.status_code is 200:
                    break

        return self.__insert2db(r.text, venue) # State machine

    def __insert2db(self, data, venue):
        # Create needed venue entries to database.
        self.dbeng.pluginCreateVenueEntity(venue.eventSQLentity())
        venueparsed = venue.parseEvents(data)
        self.dbeng.insertVenueEvents(venueparsed)

def usage():
    print "usage: bandeventnotifier.py [fetch|gigs]"
    sys.exit(1)

def main():
    dbeng = dbengine.DBEngine()

    if len(sys.argv) < 2:
        dbeng.close()
        usage()
    elif sys.argv[1] == "fetch":
        print "[-] Fetching LastFM user data."

        lfmr = lastfmfetch.LastFmRetriever(dbeng)
        [dbeng.insertLastFMartists(artist) \
                for artist in lfmr.getAllListenedBands()]
        print "[+] LastFM data fetched."

        print "[-] Fetching venues data."
        fetchqueue = Queue()
        venues = load_venue_plugins()
        for v in range(MAX_THREADS):
            t = Fetcher(fetchqueue, dbeng)
            t.setDaemon(True)
            t.start()
        for venue in venues:
            fetchqueue.put(venue)
        fetchqueue.join()
        print "[+] Venues data fetched."
    elif sys.argv[2] == "gigs":
        print "Gigs you might be interested:"
        dbeng.showgigs()
    else:
        usage()

    dbeng.close()

if __name__ == '__main__':
    main()

