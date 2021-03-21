#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import datetime
import json
import re
from typing import Any, Dict, Generator

from venues.abstract_venue import AbstractVenue, IncorrectVenueImplementation


class Klubi(AbstractVenue):
    def __init__(self):
        super().__init__()
        self.url = "http://www.tullikamari.net/fi/tapahtumat"
        self.name = "Klubi"
        self.city = "Tampere"
        self.country = "Finland"

    def parse_date_from_epoc(self, date: float):
        return datetime.datetime.fromtimestamp(date).strftime("%Y-%m-%d")

    def parse_artists(self, artists: str) -> str:
        if artists is None:
            return ""
        return ", ".join([artist["nimi"] for artist in json.loads(artists)])

    def parse_price(self, e: Dict[str, str]):
        from_door = e["hinta"] if e["hinta"] is not None else 0
        return "{}/{}€".format(e["ennakkolipun_hinta"], from_door)

    def parse_event(self, e: Dict[str, str]) \
            -> Dict[str, Any]:
        date = self.parse_date_from_epoc(int(e["aika_alku"]))
        title = e["otsikko"].rstrip(":")
        artist = self.parse_artists(e["artistit"])
        desc = json.loads(e["kuvaus"]).get("summary")
        price = self.parse_price(e)

        return {"venue": self.get_venue_name(),
                "date": date,
                "name": re.sub("\s+", " ", f"{title}: {artist} {desc}"),
                "price": price}

    def parse_events(self, data: bytes) \
            -> Generator[Dict[str, Any], None, None]:
        events_line_pattern = re.compile(r"^\s+\$scope.events = ")
        events = None
        for line in data.decode("utf-8").split("\n"):
            if re.search(events_line_pattern, line):
                events = line
                break
        if events is None:
            raise IncorrectVenueImplementation("Parsing Klubi failed")
        normalized = re.sub(events_line_pattern, "", events).rstrip(";\r")
        doc = json.loads(normalized)

        for e in doc:
            if e["tila"] == "Klubi":
                yield self.parse_event(e)


if __name__ == '__main__':
    import requests

    k = Klubi()
    r = requests.get(k.url)

    for e in k.parse_events(r.content):
        for k, v in e.items():
            print(f"{k:>10s}: {v}")
        print()
