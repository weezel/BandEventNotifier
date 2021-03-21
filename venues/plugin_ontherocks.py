#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
from typing import Any, Dict, Generator

import lxml.html

from venues.abstract_venue import AbstractVenue


class PluginParseError(Exception): pass


class Ontherocks(AbstractVenue):
    def __init__(self):
        super().__init__()
        self.url = "https://www.rocks.fi/tapahtumat/"
        self.name = "On The Rocks"
        self.city = "Helsinki"
        self.country = "Finland"

        # Parsing patterns
        self.datepat = re.compile("[0-9]{,2}.[0-9]{,2}.[0-9]{4}")
        self.pricepat = re.compile("[0-9,]+/[0-9,]+")

    def parse_price(self, parsed_price):
        if parsed_price is not None:
            price = re.search(self.pricepat, parsed_price)
            if price:
                return price.group()
        return "0"

    def parse_date(self, tag):
        date = re.search(self.datepat, tag)
        if date is None:
            return ""

        day, month, year = date.group().split(".")
        return "%.4d-%.2d-%.2d" % (int(year), int(month), int(day))

    def parse_event(self, tag) -> Dict[str, Any]:
        """
        > artist
        parsed.xpath('//div[@class="entry-content"]/h1/a/text()')
        > date
        parsed.xpath('//div[@class="entry-content"]/span[contains(@class, "entry-details")]/span/text()')
        > ticket price:
        <div class="ticket-info"> / span
        """
        datedata = " ".join(
            tag.xpath('./div[@class="entry-content"]'
                      + '/span[contains(@class, "entry-details")]/span/text()'))
        date = self.parse_date(datedata)
        artist = " ".join(tag.xpath(
            './div[@class="entry-content"]'
            + '/h1/a/text()'))
        artist = artist.strip()
        parsed_price = "".join(tag.xpath(
            './div[@class="ticket-info"]'
            + '/span/text()'))
        price = self.parse_price(parsed_price)

        return {"venue": self.get_venue_name(),
                "date": date,
                "name": artist,
                "price": f"{price}"}

    def parse_events(self, data: bytes) \
            -> Generator[Dict[str, Any], None, None]:
        doc = lxml.html.fromstring(data)
        eventtags = doc.xpath("//div[@class='tapahtuma-inner']")

        for et in eventtags:
            yield self.parse_event(et)


if __name__ == '__main__':
    import requests

    k = Ontherocks()
    r = requests.get(k.url)

    for e in k.parse_events(r.content):
        for k, v in e.items():
            print(f"{k:>10s}: {v}")
        print()
