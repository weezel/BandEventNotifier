import argparse
import datetime
import json
import os
import signal
import sys
import time

import dbengine
import utils
import venuefetcher
from lastfmapi import LastFMFetcher


def signal_handler(signal_num: int, frame):
    print("Aborting...")
    sys.exit(1)


def fetch_venues(dbeng: dbengine.DBEngine) -> None:
    started = time.perf_counter()
    print("[+] Fetching venues events.")
    vf = venuefetcher.VenueFetcher(dbeng)
    vf.fetch_venues()
    print(f"[=] Venues events added into the database. Took {time.perf_counter() - started:.2f} sec")


def fetch_lastfm(dbeng: dbengine.DBEngine) -> None:
    started = time.perf_counter()
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
    print(f"[=] Fetched listened artists from LastFM. Took {time.perf_counter() - started:.2f} sec")


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
        print("[{}] {}, {}\n{}".format(
            gigdate,
            utils.colorize(event["venue_name"], "cyan"),
            utils.colorize(event["city"], "cyan"),
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

    started = time.perf_counter()
    dbeng = dbengine.DBEngine()

    if args.gigs:
        show_gigs(dbeng)
    elif args.purge:
        print("Purging past events...")
        dbeng.purge_old_events()
    elif args.lastfm:
        fetch_lastfm(dbeng)
    elif args.venues:
        fetch_venues(dbeng)
    elif args.all:
        fetch_venues(dbeng)
        fetch_lastfm(dbeng)

    dbeng.close()

    print(f">>> Overall it took {time.perf_counter() - started:.2f} sec")


if __name__ == '__main__':
    # Allow CTRL+C termination
    signal.signal(signal.SIGINT, signal_handler)
    main()
