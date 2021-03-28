#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import datetime
import json
import re
from typing import Any, Dict, Generator

from venues.abstract_venue import AbstractVenue, IncorrectVenueImplementation


class Pakkahuone(AbstractVenue):
    def __init__(self):
        super().__init__()
        self.url = "http://www.tullikamari.net/fi/tapahtumat"
        self.name = "Pakkahuone"
        self.city = "Tampere"
        self.country = "Finland"

    def parseDateFromEpoc(self, date):
        return datetime.datetime.fromtimestamp(date).strftime("%Y-%m-%d")

    def parseArtists(self, artists):
        if artists is None:
            return ""
        return ", ".join([artist["nimi"] for artist in json.loads(artists)])

    def parsePrice(self, e):
        from_door = e["hinta"] if e["hinta"] is not None else 0
        return "{}/{}€".format(e["ennakkolipun_hinta"], from_door)

    def parse_event(self, e):
        date = self.parseDateFromEpoc(int(e["aika_alku"]))
        title = e["otsikko"].rstrip(":")
        artist = self.parseArtists(e["artistit"])
        desc = json.loads(e["kuvaus"]).get("summary")
        price = self.parsePrice(e)

        return {"venue": self.get_venue_name(),
                "date": date,
                "name": re.sub("\s+", " ", f"{title}: {artist} {desc}"),
                "price": price}

    def parse_events(self, json_data: bytes) -> Generator[Dict[str, Any], None, None]:
        events_line_pattern = re.compile(r"^\s+\$scope.events = ")
        events = None
        for line in json_data.decode("utf-8").split("\n"):
            if re.search(events_line_pattern, line):
                events = line
                break
        if events is None:
            raise IncorrectVenueImplementation("Parsing Pakkahuone failed")
        normalized = re.sub(events_line_pattern, "", events).rstrip(";\r")
        doc = json.loads(normalized)

        for e in doc:
            if e["tila"] == "Pakkahuone":
                yield self.parse_event(e)


if __name__ == '__main__':
    import requests

    p = Pakkahuone()
    r = requests.get(p.url)

    for e in p.parse_events(r.content):
        for k, v in e.items():
            print(f"{k:>10s}: {v}")
        print()
