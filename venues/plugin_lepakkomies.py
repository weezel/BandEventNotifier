#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import lxml.html

import re
import time

from venues.abstract_venue import AbstractVenue


class PluginParseError(Exception):
    pass


class Lepakkomies(AbstractVenue):
    def __init__(self):
        # XXX Apparently they have a Facebook page and then Meteli.
        # Let's rely on the latter one.
        super().__init__()
        self.url = "http://www.meteli.net/lepakkomies"
        self.name = "Lepakkomies"
        self.city = "Helsinki"
        self.country = "Finland"

        # Parsing patterns
        self.monetaryp = re.compile("[0-9]+")

    def parse_price(self, line):
        tmp = re.search(self.monetaryp, line)
        if tmp:
            price = tmp.group()
            return f"{price}€"
        return "0"

    def parse_date(self, tag: str):
        month_now = time.strftime("%m")
        year = int(time.strftime("%Y"))

        if len(tag) == 0:
            return ""

        day, month = tag.rstrip(".").split(".")
        # Are we on the new year already?
        if int(month) < int(month_now):
            year += 1

        return "%.4d-%.2d-%.2d" % (int(year), int(month), int(day))

    def parse_event(self, tag: lxml.html.HtmlElement):
        datedata = " ".join(tag.xpath('.//span[contains(@class, ' +
                                      '"event-date")]/span/text()'))
        date = self.parse_date(datedata)
        artist = " ".join(tag.xpath('.//span[contains(@class, ' +
                                    '"event-info")]/h2/text()'))
        price = " ".join(tag.xpath('.//span[contains(@class, ' +
                                   '"price")]/text()'))

        return {"venue": self.get_venue_name(),
                "date": date,
                "name": f"{artist}",
                "price": self.parse_price(price)}

    def parse_events(self, data: str):
        doc = lxml.html.fromstring(data)
        eventtags = doc.xpath('//div[@class="event-list"]')

        for et in eventtags:
            yield self.parse_event(et)


if __name__ == '__main__':
    import requests

    k = Lepakkomies()
    r = requests.get(k.url)

    for e in k.parse_events(r.content):
        for k, v in e.items():
            print(f"{k:>10s}: {v}")
        print()
