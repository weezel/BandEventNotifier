#!/usr/bin/env python3
from typing import Any, Dict, Generator

from lxml import html

import time
import re

from venues.abstract_venue import AbstractVenue


class PluginParseError(Exception): pass


class Yotalo(AbstractVenue):
    def __init__(self):
        super().__init__()
        self.url = "http://www.yo-talo.fi"
        self.name = "Yo-talo"
        self.city = "Tampere"
        self.country = "Finland"

        # Parsing patterns
        self.datestartpat = re.compile(" \d+\.\d+.$")
        self.monetarypattern = re.compile("[0-9.,]+([ ])?e(uroa)?")

    def parse_price(self, line: str) -> str:
        # FIXME Regexp is broken, fit it at some point
        # Spotted at these possible monetary variations:
        #   12 euroa
        #   12e
        #   12 EUROA
        #   12 Euroa
        prices = re.findall("[0-9.,]+ ?e(uroa)?", line, flags=re.IGNORECASE)
        return "{}€".format("/".join(prices))

    def parse_date(self, line: str) -> str:
        year = int(time.strftime("%Y"))
        month_now = time.strftime("%m")

        if line is None:
            return ""

        date = re.search(self.datestartpat, " ".join(line))
        if date is None:
            return ""

        date = date.group().lstrip(" ").rstrip(".")
        day, month = date.split(".")

        # Year has changed since the parsed month is smaller than the current
        # month.
        if int(month) < int(month_now):
            year += 1

        return "{:4d}-{:2d}-{:2d}".format(year, int(month), int(day))

    def parse_event(self, tag) -> Dict[str, Any]:
        desc = ""

        date = self.parse_date(tag.xpath('./div[@class="item_left"]/text()'))
        title = " ".join(tag.xpath('./div[@class="item_center"]/h3/a/text()'))
        for a in tag.xpath('./div[@class="item_center"]/p'):
            desc += " " + " ".join(a.xpath('./*/text()'))
        desc = re.sub("\s+", " ", desc)
        desc = desc.lstrip(" ").rstrip(" ")
        name = "%s - %s" % (title, desc)
        name = re.sub("\s+", " ", name)
        price = self.parse_price(name)

        return {"venue": self.get_venue_name(),
                "date": date,
                "name": name,
                "price": price}

    def parse_events(self, data: bytes) -> Generator[Dict[str, Any], None, None]:
        doc = html.fromstring(data)

        for item in doc.xpath('//div[@id="left"]/div[@class="item"]'):
            yield self.parse_event(item)


if __name__ == '__main__':
    import requests

    y = Yotalo()
    r = requests.get(y.url)

    for e in y.parse_events(r.content):
        for k, v in e.items():
            print(f"{k:>10s}: {v}")
        print()
