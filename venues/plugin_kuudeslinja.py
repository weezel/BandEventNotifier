#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re
import time
from typing import Any, Dict, Generator

import lxml.html

from venues.abstract_venue import AbstractVenue


class PluginParseError(Exception):
    pass


# FIXME This is boken, doesn't print anything
class Kuudeslinja(AbstractVenue):
    def __init__(self):
        super().__init__()
        self.url = "http://www.kuudeslinja.com/"
        self.name = "Kuudeslinja"
        self.city = "Helsinki"
        self.country = "Finland"

        # Parsing patterns
        self.datepat = re.compile("[0-9.]+")

    def parse_price(self, tag: str) -> str:
        # TODO Lacking implementation
        return "0"

    def parse_date(self, tag):
        month_now = time.strftime("%m")
        year = int(time.strftime("%Y"))
        ttag = " ".join(tag)
        d = re.sub("\s+", " ", ttag)
        d = d.rstrip(" ")
        d = d.split(" ")

        if len(d) != 2:
            return ""

        day, month = d[1].rstrip(".").split(".")
        # Are we on the new year already?
        if int(month) < int(month_now):
            year += 1

        return "%.4d-%.2d-%.2d" % (int(year), int(month), int(day))

    def parse_event(self, tag: lxml.html.HtmlElement) \
            -> Dict[str, Any]:
        price = ""
        date = self.parse_date(tag.xpath('./span[@class="pvm"]/text()'))
        event = " ".join(tag.xpath('./span[@class="title"]/text()'))
        event = event

        return {"venue": self.get_venue_name(),
                "date": date,
                "name": event,
                "price": price}

    def parse_events(self, data: bytes) \
            -> Generator[Dict[str, Any], None, None]:
        doc = lxml.html.fromstring(data)

        for event in doc.xpath('/html/body/div/div/div/a'):
            yield self.parse_event(event)


if __name__ == '__main__':
    import requests

    k = Kuudeslinja()
    r = requests.get(k.url)

    for e in k.parse_events(r.content):
        for k, v in e.items():
            print(f"{k:>10s}: {v}")
        print()
