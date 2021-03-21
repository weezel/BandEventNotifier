#!/usr/bin/env python3

import datetime
import re
from typing import Any, Dict, Generator

import lxml.html

from venues.abstract_venue import AbstractVenue


class PluginParseError(Exception): pass


class Glivelabtampere(AbstractVenue):
    def __init__(self):
        super().__init__()
        self.url = "https://www.glivelab.fi/tampere/"
        self.name = "G Livelab Tampere"
        self.city = "Tampere"
        self.country = "Finland"

    def parse_date(self, tag: str):
        year = datetime.datetime.now().year
        day, month, _ = tag.split(".")
        return "%.4d-%.2d-%.2d" % (int(year), int(month), int(day))

    def normalize_string(self, s: str):
        rm_spaces = re.sub("\+s", " ", s)
        rm_left_padding = re.sub("^\s+", "", rm_spaces)
        rm_right_padding = re.sub("\s+$", "", rm_left_padding)
        return rm_right_padding

    def parse_event(self, tag: lxml.html.HtmlElement) \
            -> Dict[str, Any]:
        for node in tag:
            # XXX I have no idea why the xpath mentioned in parseEvents()
            # doesn't work as intended. I cannot see two 'div' child nodes with
            # 'a' as a parent as I would expect.
            #
            # Hence, go back one node and list all of it's descendants.
            prev_nodes = node.xpath('../*')
            if len(prev_nodes) != 2:
                raise PluginParseError("Failed to parse GliveLab Tampere")
            # First node is "img-wrapper" which we are not interested
            title = " ".join(prev_nodes[1].xpath('./div/h2/text()'))
            title = self.normalize_string(title)
            date = " ".join(prev_nodes[1].xpath('./div/div[@class="date"]/text()'))
            date = self.parse_date(self.normalize_string(date))
            time = " ".join(prev_nodes[1].xpath('./div/div[@class="time"]/text()'))
            time = self.normalize_string(time)

            price = "0€"

            return {"venue": self.get_venue_name(),
                    "date": date,
                    "name": title,
                    "price": price}

    def parse_events(self, data: bytes) \
            -> Generator[Dict[str, Any], None, None]:
        doc = lxml.html.fromstring(data)
        eventtags = doc.xpath('//li[@class="item"]/a')

        for et in eventtags:
            yield self.parse_event(et)


if __name__ == '__main__':
    import requests

    g = Glivelabtampere()
    r = requests.get(g.url)

    for e in g.parse_events(r.content):
        for k, v in e.items():
            print(f"{k:>10s}: {v}")
        print()
