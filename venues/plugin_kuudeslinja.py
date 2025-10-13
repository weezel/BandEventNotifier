#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import http
import re
import time
from typing import Any, Dict, Generator, List

import lxml.html

import fetcher
from venues.abstract_venue import AbstractVenue


class Kuudeslinja(AbstractVenue):
    def __init__(self):
        super().__init__()
        self.url = "http://www.kuudeslinja.com/"
        self.name = "Kuudeslinja"
        self.city = "Helsinki"
        self.country = "Finland"
        self.day_pat = r"[0-9]+\.[0-9]+"

    def parse_date(self, date_tag: List[str]) -> str:
        year = int(time.strftime("%Y"))
        this_month = int(time.strftime("%m"))
        parsed_date = re.search(self.day_pat, "".join(date_tag))
        day, month = parsed_date.group().split(sep=".", maxsplit=2)
        day, month = int(day), int(month)
        # Year wrapped
        if month < this_month:
            year += 1

        return f"{year:04d}-{month:02d}-{day:02d}"

    def parse_event(self, tag: lxml.html.HtmlElement) \
            -> Dict[str, Any]:
        date = self.parse_date(tag.xpath('./div[@class="pvm"]/text()'))
        title = " ".join(tag.xpath('./div[@class="title"]/text()'))
        info = " ".join(tag.xpath('./div[@class="info"]/text()'))
        price = self.parse_price(info)
        event = f"{title}: {info}".replace("\n", "")

        return {
            "venue": self.name,
            "date": date,
            "name": event,
            "price": price
        }

    def parse_events(self, data: bytes) \
            -> Generator[Dict[str, Any], None, None]:
        doc = lxml.html.fromstring(data)

        for event in doc.xpath('/html/body/main/section[@class="events"]/article[@class="event"]'):
            yield self.parse_event(event)


if __name__ == '__main__':
    k = Kuudeslinja()
    r = fetcher.retry_request(http.HTTPMethod.GET, k.url)

    for e in k.parse_events(r.content):
        for k, v in e.items():
            print(f"{k:>10s}: {v}")
        print()
