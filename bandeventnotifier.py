#!/usr/bin/env python
# -*- coding: utf-8 -*-

import glob
import os
import pickle
import requests
import sys
import threading
import time
from Queue import Queue

import dbengine
from plugin_handler import load_venue_plugins
import lastfmfetch
import utils

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
            print "[+] Fetching and parsing '%s' venue" % (venue.name)
            venuehtml = self.__fetch(venue)

            venueparsed = list()
            try:
                for i in venue.parseEvents(venuehtml):
                    venueparsed.append(i)
            except TypeError, te:
                print "%s Error while parsing %s plugin" % \
                        (utils.colorize("/_!_\\", "red"),    \
                         venue.getVenueName())
                self.fetchqueue.task_done()

            # XXX Pickle hack to dodge SQLite concurrency problems.
            venue.parseddata = venueparsed
            fname = os.path.join("venues", venue.__class__.__name__ + ".pickle")
            pickle.dump(venue, open(fname, "wb"))

            self.fetchqueue.task_done()

    def __fetch(self, venue):
        retries = 3
        r = requests.get(venue.url)

        if r.status_code is not 200:
            for retry in range(0, retries):
                print "Couldn't connect %s, retrying %d/%d..." % \
                        (venue.url, retry + 1, retries)
                r = requests.get(venue.url)

                if r.status_code is 200:
                    break
        return r.content

def insert2db(dbeng):
    # Create needed venue entries to database.
    # XXX Remove pickle handler once concurrency problems are fixed.

    # And here we load the venues again, yes annoying. More memory/CPU
    # efficient implementation on it's way.
    for fname in glob.iglob("venues/*.pickle"):
        venue = pickle.load(open(fname, "rb"))
        # Create needed entries in venue table
        dbeng.pluginCreateVenueEntity(venue.eventSQLentity())

        for v in venue.parseddata:
            dbeng.insertVenueEvents(v)
        # Remove pickle file
        os.remove(fname)

def usage():
    print "usage: bandeventnotifier.py [fetch[lastfm|venues]|gigs|purge]"
    sys.exit(1)

def main():
    dbeng = dbengine.DBEngine()

    if len(sys.argv) < 2:
        dbeng.close()
        usage()
    elif sys.argv[1] == "fetch":
        if len(sys.argv) < 3:
            print "fetch: [lastfm|venues]"
            usage()
        elif sys.argv[2] == "lastfm":
            print "[+] Fetching LastFM user data."
            lfmr = lastfmfetch.LastFmRetriever(dbeng)
            for artist in lfmr.nonAPIparser():
                dbeng.insertLastFMartists(artist)
            print "[=] LastFM data fetched."
        elif sys.argv[2] == "venues":
            print "[+] Fetching venues data."
            fetchqueue = Queue()
            venues = load_venue_plugins()
            for v in range(MAX_THREADS):
                t = Fetcher(fetchqueue, dbeng)
                t.setDaemon(True)
                t.start()
            for venue in venues:
                fetchqueue.put(venue)
            fetchqueue.join()
            print "[=] Venues data fetched."

            print "[+] Inserting into a database..."
            insert2db(dbeng)
            print "[=] Venues added into the database."
        else:
            usage()
    elif sys.argv[1] == "gigs":
        today = time.strftime("%Y-%m-%d")
        print utils.colorize("GIGS YOU MIGHT BE INTERESTED:", "underline")

        for event in dbeng.getAllGigs():
            for artist in dbeng.getArtists():
                printEvent = False
                artistname = artist["artist"].lower().split(" ")
                eventartists = event[3].lower()

                # Singly worded artist name
                if len(artistname) ==  1:
                    if artistname[0] in eventartists.split(" "):
                        printEvent = True
                # More than one word in artist's name
                else:
                    if " ".join(artistname) in eventartists:
                        printEvent = True

                if printEvent:
                    print utils.colorize("MATCH: %s, PLAYCOUNT: %d" % \
                            (artist["artist"],                        \
                             artist["playcount"]),                    \
                            "yellow")
                    if event[0] == today:
                        gigdate = utils.colorize(event[0], "green")
                    else:
                        gigdate = utils.colorize(event[0], "bold")
                    print u"[%s] %s, %s\n%s\n" % \
                            (gigdate, utils.colorize(event[1], "cyan"), \
                             event[2], event[3])
                    break # We are done, found already a matching artist

    elif sys.argv[1] == "purge":
        print "Purging past events..."
        dbeng.purgeOldEvents()
    else:
        usage()

    dbeng.close()

if __name__ == '__main__':
    main()

