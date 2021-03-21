#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re

import lxml.html

from venues.abstract_venue import AbstractVenue


class PluginParseError(Exception): pass


class Olympia(AbstractVenue):
    def __init__(self):
        super().__init__()
        self.url = "http://olympiakortteli.fi/keikat/"
        self.name = "Olympia-kortteli"
        self.city = "Tampere"
        self.country = "Finland"

        # Parsing patterns
        self.datepat = re.compile("[0-9.]+")
        self.monetary = re.compile("[0-9]+(\s+)?€")

    def parse_price(self, t):
        # XXX Fix this
        return 0
        # tag = t.xpath('./div[2]/strong/text()')

        # foundprice = re.findall(self.monetary, " ".join(tag))

        # if foundprice is None:
        #    foundprice = ""

        # return "0" if len(foundprice) == 0 else "%s" % (foundprice[0])

    def parse_date(self, t):
        tag = t.xpath('./div[2]/text()')

        if tag:
            tag = " ".join(tag)
            tag = re.sub("\s+", " ", tag).lstrip(" ").rstrip(" ")

        founddate = re.search(self.datepat, tag)

        if founddate is None:
            return ""

        day, month, year = founddate.group().split(".")
        return "%.4d-%.2d-%.2d" % (int(year), int(month), int(day))

    def parse_events(self, data: str):
        doc = lxml.html.fromstring(data)

        for event in doc.xpath('//div[contains(@class, "keikkalista")]/div'):
            name = "".join(event.xpath("./div/h3/text()"))
            name = re.sub("\s+", " ", name).lstrip(" ").rstrip(" ")
            date = self.parse_date(event)
            price = self.parse_price(event)

            yield {"venue": self.get_venue_name(),
                   "date": date,
                   "name": name,
                   "price": price}


if __name__ == '__main__':
    import requests

    l = Olympia()
    r = requests.get(l.url)

    for e in l.parse_events(r.content):
        for k, v in e.items():
            print(f"{k:>10s}: {v}")
        print()
