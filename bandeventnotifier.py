#!bin/python3
# -*- coding: utf-8 -*-

import datetime
import glob
import os
import requests
import signal
import sys
import threading
import time
from queue import Queue

import dbengine
from plugin_handler import load_venue_plugins
from lastfmfetch import LastFmRetriever
import utils

MAX_THREADS = 20
MIN_PLAYCOUNT = 9


def signal_handler(signal, frame):
    print("Aborting...")
    sys.exit(1)


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
            print(f"[+] Fetching and parsing venue '{venue.name}'")
            venuehtml = self.__fetch(venue)

            if venuehtml == "":
                self.fetchqueue.task_done()

            venueparsed = list()
            try:
                for i in venue.parseEvents(venuehtml):
                    if i is None or len(i) == 0:
                        print(f"Couldn't parse venue: {venue.getVenueName()}")
                        self.fetchqueue.task_done()
                        return
                    venueparsed.append(i)
            except TypeError as te:
                print("{} Error while parsing {} venue".format(
                    (utils.colorize("/_!_\\", "red"), venue.getVenueName())))
                self.fetchqueue.task_done()
                return

            venue.parseddata = venueparsed
            self.fetchqueue.task_done()

    def __fetch(self, venue):
        retries = 3
        sleeptimesec = 5.0
        try:
            r = requests.get(venue.url)
        except Exception as general_err:
            print(f"ERROR: {general_err}")
            return ""

        # TODO Check r.ok
        if r.status_code == 404:
            print(f"{venue.url} is broken, please fix it.")
            return ""
        elif r.status_code != 200:
            for retry in range(0, retries):
                print(f"Couldn't connect {venue.name}[{venue.city}] {venue.url}, ", end="")
                print(f"retrying in {sleeptimesec:.0f} seconds [{retry + 1:1d}/{retries:2d}]...")
                time.sleep(sleeptimesec)
                r = requests.get(venue.url, timeout=5)

                if r.status_code == 200:
                    break
        return r.content


def usage():
    print("usage: bandeventnotifier.py [fetch [lastfm|venues] | gigs | html filename | purge]")
    sys.exit(1)


def main():
    if not os.path.exists(dbengine.dbname):
        dbengine.init_db()

    dbeng = dbengine.DBEngine()

    if len(sys.argv) < 2:
        dbeng.close()
        usage()
    elif sys.argv[1] == "fetch":
        if len(sys.argv) < 3:
            print("fetch: [lastfm|venues]")
            usage()
        elif sys.argv[2] == "lastfm":
            print("[+] Fetching LastFM user data.")
            all_bands = dict()
            lfm_queue = Queue()
            lfmr = LastFmRetriever(lfm_queue, all_bands)
            pages = lfmr.getPaginatedPages()

            for v in range(MAX_THREADS):
                t = LastFmRetriever(lfm_queue, all_bands)
                t.setDaemon(True)
                t.start()
            for page in pages:
                lfm_queue.put(page)
            lfm_queue.join()

            for artist, playcount in lfmr.getArtistsPlaycounts():
                dbeng.insertLastFMartists(artist, playcount)
            print("[=] LastFM data fetched.")
        elif sys.argv[2] == "venues":
            print("[+] Fetching venues data.")
            fetchqueue = Queue()
            venues = load_venue_plugins()
            for v in range(MAX_THREADS):
                t = Fetcher(fetchqueue, dbeng)
                t.setDaemon(True)
                t.start()
            for venue in venues:
                fetchqueue.put(venue)
            fetchqueue.join()
            print("[=] Venues data fetched.")

            print("[+] Inserting into a database...")
            dbeng.pluginCreateVenueEntity(venue.eventSQLentity())

            for v in venue.parseddata:
                dbeng.insertVenueEvents(v)
            print("[=] Venues added into the database.")
        else:
            usage()
    elif sys.argv[1] == "gigs":
        weektimespan = datetime.datetime.now() + datetime.timedelta(days=7)
        print(utils.colorize("GIGS YOU MIGHT BE INTERESTED:", "underline"))

        for event in dbeng.getAllGigs():
            for artist in dbeng.getArtists():
                printEvent = False
                artistname = artist["artist"].lower().split(" ")
                eventartists = event[3].lower()

                # Singly worded artist name
                if len(artistname) == 1:
                    if artistname[0] in eventartists.split(" "):
                        printEvent = True
                # More than one word in artist's name
                else:
                    if " ".join(artistname) in eventartists:
                        printEvent = True

                # Don't show artists that have been listened only a few times
                # (miss shots likely).
                if artist["playcount"] < MIN_PLAYCOUNT:
                    printEvent = False

                if printEvent:
                    print(utils.colorize("MATCH: {}, PLAYCOUNT: {:d}".format( \
                        artist["artist"], \
                        artist["playcount"]), \
                        "yellow"))
                    if datetime.datetime.strptime(event[0], "%Y-%m-%d") <= \
                            weektimespan:
                        gigdate = utils.colorize(event[0], "red")
                    else:
                        gigdate = utils.colorize(event[0], "bold")
                    print("[{}] {}, {}".format( \
                        gigdate, \
                        utils.colorize(event[1], "cyan"), \
                        event[2]))
                    print("{}\n".format(event[3]))
                    break  # We are done, found already a matching artist
    elif sys.argv[1] == "html":
        if len(sys.argv) < 3:
            print("ERROR: Missing output HTML filename")
            usage()
        with open(sys.argv[2], "w") as f:
            f.write("<html>")
            f.write('<meta charset="UTF-8">')
            f.write(' <meta name="viewport" content="width=device-width, initial-scale=1.0">')
            f.write("""
<style>
body {
    background-color: darkgrey;
}
table, th, td {
  border: 1px solid black;
  border-collapse: collapse;
}
th, td {
  padding: 15px;
}
</style>
        """)
            f.write('<table style="width=100%">')
            f.write('  <tr>')
            f.write('    <th>Matched artist</th>')
            f.write('    <th>Playcount</th>')
            f.write('    <th>Event date</th>')
            f.write('    <th>Venue</th>')
            f.write('    <th>Description</th>')
            f.write('  </tr>')
            for event in dbeng.getAllGigs():
                for artist in dbeng.getArtists():
                    printEvent = False
                    artistname = artist["artist"].lower().split(" ")
                    eventartists = event[3].lower()

                    # Singly worded artist name
                    if len(artistname) == 1:
                        if artistname[0] in eventartists.split(" "):
                            printEvent = True
                    # More than one word in artist's name
                    else:
                        if " ".join(artistname) in eventartists:
                            printEvent = True

                    # Don't show artists that have been listened only a few times
                    # (miss shots likely).
                    if artist["playcount"] < MIN_PLAYCOUNT:
                        printEvent = False

                    if printEvent:
                        f.write('  <tr>')
                        f.write(f'    <td>{artist["artist"]}</td>')
                        f.write(f'    <td>{artist["playcount"]:d}</td>')
                        f.write(f'    <td>{event[0]} </td>')
                        f.write(f'    <td>{event[1]}, {event[2]}</td>')
                        f.write(f'    <td>{event[3]}</td>')
                        f.write('  </tr>')
                        break  # We are done, found already a matching artist
            f.write("</table>")
            f.write("</html>\n")
    elif sys.argv[1] == "purge":
        print("Purging past events...")
        dbeng.purgeOldEvents()
    else:
        usage()

    dbeng.close()


if __name__ == '__main__':
    # Allow CTRL+C termination
    signal.signal(signal.SIGINT, signal_handler)
    main()
