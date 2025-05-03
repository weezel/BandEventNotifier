import argparse
import datetime
import json
import os
import signal
import sys
import threading
import time
from queue import Queue

import requests

import dbengine
import utils
from lastfmapi import LastFMFetcher
from lastfmfetch import LastFmRetriever
from plugin_handler import load_venue_plugins
from venues.abstract_venue import AbstractVenue

MAX_THREADS = 20
MIN_PLAYCOUNT = 9

requests_user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/113.0"


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
            r = requests.get(venue.url, headers={"User-Agent": requests_user_agent})
        except Exception as general_err:
            print(f"ERROR: {general_err}")
            return bytes("")

        # TODO Check r.ok
        if r.status_code == 404:
            print(f"{venue.url} is broken, please fix it.")
            return "".encode("utf8")
        elif not r.ok:
            for retry in range(0, retries):
                print(f"Couldn't connect {venue.name}[{venue.city}] {venue.url}, status code was {r.status_code}, ",
                      end="")
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
        t.daemon = True
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
    print("[+] Fetching listened artists from LastFM")
    lfm_creds = {}
    with open("lastfm_creds.json", "r", encoding="utf-8") as f:
        lfm_creds = json.load(f)
    if lfm_creds is None:
        print("Couldn't read lastfm_creds.json")
        sys.exit(1)

    lfm = LastFMFetcher(
        username=lfm_creds["username"],
        password=lfm_creds["password"],
        api_key=lfm_creds["api_key"],
        api_secret=lfm_creds["api_secret"],
    )
    lfm.fetch_and_store_all_artists(dbeng.get_conn())
    print("[=] Fetched listened artists from LastFM")


def show_gigs(dbeng: dbengine.DBEngine) -> None:
    weektimespan = datetime.datetime.now() + datetime.timedelta(days=7)
    print(utils.colorize("GIGS YOU MIGHT BE INTERESTED:", "underline"))
    for event in dbeng.get_relevant_gigs():
        print(f"{utils.colorize('MATCH:', 'yellow')} {event['matching_artists']}")
        if datetime.datetime.strptime(event["date"], "%Y-%m-%d") <= \
                weektimespan:
            gigdate = utils.colorize(event["date"], "red")
        else:
            gigdate = utils.colorize(event["date"], "bold")
        print("[{}] {}\n{}".format(
            gigdate,
            utils.colorize(event["venue_name"], "cyan"),
            event["event_name"]),
        )
        print()


def main() -> None:
    argparser = argparse.ArgumentParser()
    argparser.add_argument("--gigs", help="Show coming gigs", action="store_true")
    argparser.add_argument("--purge", help="Purge gone gigs", action="store_true")

    sub_parser = argparser.add_subparsers(help="Fetch venues performers or lastfm listening stats")
    fetch_parser = sub_parser.add_parser("fetch", help="Fetch options")
    mut = fetch_parser.add_mutually_exclusive_group()
    mut.add_argument("--lastfm", help="Fetch LastFM listening stats", action="store_true")
    mut.add_argument("--venues", help="Fetch and parse venues events", action="store_true")
    mut.add_argument("--all", help="Fetch venues and LastFM artists", action="store_true")

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
    elif args.all:
        feth_venues(dbeng)
        fetch_lastfm(dbeng)

    dbeng.close()


if __name__ == '__main__':
    # Allow CTRL+C termination
    signal.signal(signal.SIGINT, signal_handler)
    main()
