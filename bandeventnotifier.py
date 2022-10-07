#!bin/python3
# -*- coding: utf-8 -*-
import argparse
import datetime
import os
import signal
import sys
import threading
import time
from queue import Queue

import requests

import dbengine
import utils
from lastfmfetch import LastFmRetriever
from plugin_handler import load_venue_plugins
from venues.abstract_venue import AbstractVenue

MAX_THREADS = 20
MIN_PLAYCOUNT = 9


def signal_handler(signal_num: int, frame):
    print("Aborting...")
    sys.exit(1)


venues_lock = threading.Lock()
parsed_venues_data = dict()


class Fetcher(threading.Thread):
    def __init__(self, q, dbeng: dbengine.DBEngine) -> None:
        threading.Thread.__init__(self)
        self.fetchqueue = q
        self.dbeng = None

        self.__db_init(dbeng)

    def __db_init(self, dbobj: dbengine.DBEngine) -> None:
        if self.dbeng is None:
            self.dbeng = dbobj

    def run(self) -> None:
        global parsed_venues_data, venues_lock

        while True:
            venue = self.fetchqueue.get()
            print(f"[+] Fetching and parsing venue '{venue.get_venue_name()}'")
            venuehtml = self._fetch(venue)

            if venuehtml == "":
                self.fetchqueue.task_done()

            try:
                for parsed_venue in venue.parse_events(venuehtml):
                    if parsed_venue is None or len(parsed_venue) == 0:
                        print(f"Couldn't parse venue: {venue.get_venue_name()}")
                        self.fetchqueue.task_done()
                        return
                    with venues_lock:
                        if venue.url not in parsed_venues_data:
                            parsed_venues_data[venue.url] = []
                        parsed_venues_data[venue.url].append(parsed_venue)
            except TypeError as te:
                print("{warn} Error while parsing {venue_name} venue: {err}".format(
                    warn=utils.colorize("/_!_\\", "red"),
                    venue_name=venue.get_venue_name(),
                    err=te))
                self.fetchqueue.task_done()
                return

            self.fetchqueue.task_done()

    # FIXME Add type
    def _fetch(self, venue: AbstractVenue) -> bytes:
        retries = 3
        sleeptimesec = 5.0
        try:
            r = requests.get(venue.url)
        except Exception as general_err:
            print(f"ERROR: {general_err}")
            return bytes("")

        # TODO Check r.ok
        if r.status_code == 404:
            print(f"{venue.url} is broken, please fix it.")
            return bytes("")
        elif r.status_code != 200:
            for retry in range(0, retries):
                print(f"Couldn't connect {venue.name}[{venue.city}] {venue.url}, ", end="")
                print(f"retrying in {sleeptimesec:.0f} seconds [{retry + 1:1d}/{retries:2d}]...")
                time.sleep(sleeptimesec)
                r = requests.get(venue.url, timeout=5)

                if r.status_code == 200:
                    break
        return r.content


def feth_venues(dbeng: dbengine.DBEngine) -> None:
    print("[+] Fetching venues events.")
    fetchqueue = Queue()
    venues = load_venue_plugins()
    for v in range(MAX_THREADS):
        t = Fetcher(fetchqueue, dbeng)
        t.setDaemon(True)
        t.start()
    for venue in venues:
        fetchqueue.put(venue)
    fetchqueue.join()
    print("[=] Venues events fetched.")
    print("[+] Inserting into a database...")
    for v in venues:
        # Add database entries for the venue
        dbeng.pluginCreateVenueEntity(v.event_sqlentity())

        if v.url not in parsed_venues_data:
            print(f"Cannot add data for {v.name}/{v.city} ({v.country}) because it's empty. Continuing...")
            continue
        parsed_venue = parsed_venues_data[v.url]
        dbeng.insertVenueEvents(v, parsed_venue)
    print("[=] Venues events added into the database.")


def fetch_lastfm(dbeng: dbengine.DBEngine) -> None:
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


def show_gigs(dbeng: dbengine.DBEngine) -> None:
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
            if int(artist["playcount"]) < MIN_PLAYCOUNT:
                printEvent = False

            if printEvent:
                print(utils.colorize("MATCH: {}, PLAYCOUNT: {:d}".format(
                    artist["artist"],
                    int(artist["playcount"])),
                    "yellow"))
                if datetime.datetime.strptime(event[0], "%Y-%m-%d") <= \
                        weektimespan:
                    gigdate = utils.colorize(event[0], "red")
                else:
                    gigdate = utils.colorize(event[0], "bold")
                print("[{}] {}, {}".format(
                    gigdate,
                    utils.colorize(event[1], "cyan"),
                    event[2]))
                print(f"{event[3]}\n")
                break  # We are done, found already a matching artist


def main() -> None:
    argparser = argparse.ArgumentParser()
    argparser.add_argument("--gigs", help="Show coming gigs", action="store_true")
    argparser.add_argument("--purge", help="Purge gone gigs", action="store_true")

    sub_parser = argparser.add_subparsers(help="Fetch venues performers or lastfm listening stats")
    fetch_parser = sub_parser.add_parser("fetch", help="Fetch options")
    mut = fetch_parser.add_mutually_exclusive_group()
    mut.add_argument("--lastfm", help="Fetch LastFM listening stats", action="store_true")
    mut.add_argument("--venues", help="Fetch and parse venues events", action="store_true")

    args = argparser.parse_args()

    if not os.path.exists(dbengine.dbname):
        dbengine.init_db()

    dbeng = dbengine.DBEngine()

    if args.gigs:
        show_gigs(dbeng)
    elif args.purge:
        print("Purging past events...")
        dbeng.purgeOldEvents()
    elif args.lastfm:
        fetch_lastfm(dbeng)
    elif args.venues:
        feth_venues(dbeng)

    dbeng.close()


if __name__ == '__main__':
    # Allow CTRL+C termination
    signal.signal(signal.SIGINT, signal_handler)
    main()
