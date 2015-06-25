#!/usr/bin/env python
# -*- coding: utf-8 -*-

import glob
import imp
import re
import requests
import sys
import threading
from Queue import Queue

from plugin_handler import load_venue_plugins

MAX_THREADS = 6


# XXX Rough implementation of parallel venue fetcher
class Fetcher(threading.Thread):
    def __init__(self, q):
        threading.Thread.__init__(self)

        self.fetchqueue = q

    def run(self):
        """docstring for run"""
        while True:
            venue = self.fetchqueue.get()
            venue_data = start_fetching(venue)
            print "[-] Fetching and parsing '%s'" % (venue.name)
            self.fetchqueue.task_done()
            # TODO Implement callback to completed venues
            #print "[+] Fetching '%s' completed" % (venue.name)


def start_fetching(venue):
    retries = 3
    r = requests.get(venue.url)

    if r.status_code is not 200:
        for retry in range(0, retries):
            print "Couldn't connect %s, retrying %d/%d..." % (venue.url, retry + 1, retries)
            r = requests.get(venue.url)
    try:
        venue.parseArtists(r.text)
    except Exception, e:
        raise e


def main():
    fetchqueue = Queue()
    venues = load_venue_plugins()
    
    for v in range(MAX_THREADS):
        t = Fetcher(fetchqueue)
        t.setDaemon(True)
        t.start()
    for venue in venues:
        fetchqueue.put(venue)
    fetchqueue.join()

if __name__ == '__main__':
    main()

