#!/usr/bin/env python3

import re
import time
from typing import Any, Dict, Generator, List

import lxml.html
import requests

from venues.abstract_venue import AbstractVenue


class Glivelabhelsinki(AbstractVenue):
    def __init__(self):
        super().__init__()
        self.url = "https://www.glivelab.fi/#events"
        self.name = "G Livelab Helsinki"
        self.city = "Helsinki"
        self.country = "Finland"

    def parse_date(self, date: List[str]) -> str:
        year = int(time.strftime("%Y"))
        this_month = int(time.strftime("%m"))
        date_column = "".join(date)
        date_column = self.normalize_string(date_column)
        day, month = date_column.rstrip(".").split(".")
        day, month = int(day), int(month)
        # Year wrapped
        if month < this_month:
            year += 1
        return "%.4d-%.2d-%.2d" % (int(year), int(month), int(day))

    def normalize_string(self, s: str) -> str:
        rm_newlines = s.replace("\n", " ")
        rm_spaces = re.sub(r"\s+", " ", rm_newlines)
        rm_left_padding = re.sub(r"^\s+", "", rm_spaces)
        rm_right_padding = re.sub(r"\s+$", "", rm_left_padding)
        return rm_right_padding

    def parse_event(self, tag: lxml.html.HtmlElement) -> Dict[str, Any]:
        date = self.parse_date(tag.xpath('./div[@class="datetime"]/div[@class="date"]/text()'))
        event_description = " ".join(tag.xpath('./div[@class="title-description"]/h2[@class="title"]/text()'))
        event_description = self.normalize_string(event_description)
        price = "0€"

        return {"venue": self.get_venue_name(),
                "date": date,
                "name": event_description,
                "price": price}

    def parse_events(self, data: bytes) -> Generator[Dict[str, Any], None, None]:
        doc = lxml.html.fromstring(data)
        eventtags = doc.xpath('/html/body/div[@id="page"]/div[@id="main"]/article[@class="page"]/article'
                              '//ul[@class="listing"]/li[@class="item"]/a/div[@class="info"]')

        for et in eventtags:
            yield self.parse_event(et)


if __name__ == '__main__':
    g = Glivelabhelsinki()
    r = requests.get(g.url)

    for e in g.parse_events(r.content):
        for k, v in e.items():
            print(f"{k:>10s}: {v}")
        print()
