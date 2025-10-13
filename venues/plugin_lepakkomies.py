#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import http
from typing import List

import lxml.html

import re
import time

import fetcher
from venues.abstract_venue import AbstractVenue


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
        self.monetaryp = re.compile("[0-9,.]+")

    def parse_date(self, tag: str):
        this_month = int(time.strftime("%m"))
        year = int(time.strftime("%Y"))

        if len(tag) == 0:
            return ""

        day, month = tag.rstrip(".").split(".")
        day = int(day)
        month = int(month)
        # Are we on the new year already?
        if month < this_month:
            year += 1

        return f"{year:04d}-{month:02d}-{day:02d}"

    def parse_price(self, prices: List[str]) -> str:
        found_prices = list()

        for p in prices:
            if (match := self.monetaryp.search(p)) is not None:
                found_prices.append(match.group())

        return "{}€".format("".join(found_prices))

    def parse_event(self, tag: lxml.html.HtmlElement):
        datedata = " ".join(tag.xpath('.//span[contains(@class, '
                                      '"event-date")]/span/text()'))
        date = self.parse_date(datedata)
        artist = " ".join(tag.xpath('.//span[contains(@class, '
                                    '"event-info")]/h2/text()'))
        price = " ".join(tag.xpath('.//span[contains(@class, '
                                   '"price")]/text()'))
        price = self.parse_price(price.split(" "))

        return {
            "venue": self.name,
            "date": date,
            "name": artist,
            "price": price,
        }

    def parse_events(self, data: bytes):
        doc = lxml.html.fromstring(data)
        eventtags = doc.xpath('//div[@class="event-list"]')

        for et in eventtags:
            yield self.parse_event(et)


if __name__ == '__main__':
    lepakkomies = Lepakkomies()
    r = fetcher.retry_request(http.HTTPMethod.GET, lepakkomies.url)

    for e in lepakkomies.parse_events(r.content):
        for lepakkomies, v in e.items():
            print(f"{lepakkomies:>10s}: {v}")
        print()
