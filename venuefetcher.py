from concurrent.futures import ThreadPoolExecutor
from typing import Any, Dict, List, Optional, Tuple

import dbengine
from fetcher import retry_request
from plugin_handler import load_venue_plugins
from venues.abstract_venue import AbstractVenue


class VenueFetcher:
    def __init__(self, dbeng: dbengine.DBEngine) -> None:
        self.dbeng = dbeng
        self.venues = load_venue_plugins()
        self._prepare_db()

    def _prepare_db(self):
        # Create database entries for the found venues
        for v in self.venues:
            self.dbeng.plugin_create_venue_entity(v.event_sqlentity())

    def fetch_venues(self):
        with ThreadPoolExecutor(max_workers=20) as executor:
            results = executor.map(self._fetch, self.venues, chunksize=10)

        for r in results:
            if r is None:
                continue

            venue, events = r
            print(f"Fetched and stored events of venue {venue.name}")
            try:
                self.dbeng.insert_venue_events(venue, events)
            except Exception as err:
                print(f"Failed to insert venue data for {venue.name} into database: {err}")

    def _fetch(self, venue: AbstractVenue) -> Optional[Tuple[AbstractVenue, List[Dict[str, Any]]]]:
        try:
            r = retry_request("GET", venue.url)
            return venue, [event for event in venue.parse_events(r.content)]
        except Exception as err:
            print(f"Error while fetching venue {venue.name}: {err}")
            return None
