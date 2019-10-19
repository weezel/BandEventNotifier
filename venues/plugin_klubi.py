#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import datetime
import json
import re
import time


class PluginParseError(Exception): pass

class Klubi(object):
    def __init__(self):
        self.url = "http://www.tullikamari.net/fi/tapahtumat"
        self.name = "Klubi"
        self.city = "Tampere"
        self.country = "Finland"

    def getVenueName(self):
        return self.name

    def getCity(self):
        return self.city

    def getCountry(self):
        return self.country

    def eventSQLentity(self):
        """
        This method is used to ensure venue exists in venue SQL table.
        """
        return { "name" : self.name, \
                 "city" : self.city, \
                 "country" : self.country }

    def parseDateFromEpoc(self, date):
        return datetime.datetime.fromtimestamp(date).strftime("%Y-%m-%d")

    def parseArtists(self, artists):
        if artists is None:
            return ""
        return ", ".join([artist["nimi"] for artist in json.loads(artists)])

    def parsePrice(self, e):
        from_door = e["hinta"] if e["hinta"] is not None else 0
        return "{}/{}€".format(e["ennakkolipun_hinta"], from_door)

    def parseEvent(self, e):
        date = self.parseDateFromEpoc(int(e["aika_alku"]))
        title = e["otsikko"].rstrip(":")
        artist = self.parseArtists(e["artistit"])
        desc = json.loads(e["kuvaus"]).get("summary")
        price = self.parsePrice(e)

        return { "venue" : self.getVenueName(),
                 "date" : date,
                 "name" : re.sub("\s+", " ", f"{title}: {artist} {desc}"),
                 "price" : price }

    def parseEvents(self, json_data):
        events_line_pattern = re.compile(r"^\s+\$scope.events = ")
        events = None
        for line in json_data.decode("utf-8").split("\n"):
            if re.search(events_line_pattern, line):
                events = line
                break
        if events == None:
            raise PluginParseError("Parsing Klubi failed")
        normalized = re.sub(events_line_pattern, "", events).rstrip(";\r")
        doc = json.loads(normalized)

        for e in doc:
            if e["tila"] == "Klubi":
                yield self.parseEvent(e)

if __name__ == '__main__':
    import requests

    k = Klubi()
    r = requests.get(k.url)

    for e in k.parseEvents(r.content):
        for k, v in e.items():
            print(f"{k:>10s}: {v}")
        print

