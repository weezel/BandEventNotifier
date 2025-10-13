#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from datetime import datetime
import time
import http
import re
from typing import Any, Dict, Generator

import lxml.html

import fetcher
from venues.abstract_venue import AbstractVenue


class Aanivalli(AbstractVenue):
    def __init__(self):
        super().__init__()
        self.url = "https://aaniwalli.fi//"
        self.name = "Äänivalli"
        self.city = "Helsinki"
        self.country = "Finland"

        # Parsing patterns
        self.datepat = re.compile("[0-9.]{1,2}\\.[0-9]{1,2}")

    def parse_date(self, tag: lxml.html.HtmlElement) -> str:
        pvm_tag = "".join(tag.xpath('.//div[@class="pills"]/span')[0].text)
        if (parsed_pvm := self.datepat.search(pvm_tag)) is not None:
            day, month = parsed_pvm.group().split(".")
            day = int(day)
            month = int(month)
            year = datetime.now().year
            month_now = time.strftime("%m")
            if int(month) < int(month_now):
                year += 1
            return f"{year:04d}-{month:02d}-{day:02d}"

        return ""

    def parse_event(self, tag: lxml.html.HtmlElement) -> str:
        info_tag = "".join(tag.xpath('.//h1[@class="event-title"]/text()'))
        info_tag = re.sub(r"\s+", " ", info_tag).lstrip(" ").rstrip(" ")
        return info_tag

    def parse_price(self, tag: lxml.html.HtmlElement) -> str:
        # XXX Not feasible without visiting the ticket provider's site. Won't do.
        return "0€"

    def parse_events(self, data: bytes) -> Generator[Dict[str, Any], None, None]:
        doc = lxml.html.fromstring(data)

        for event in doc.xpath('//div[@class="event-wrapper"]/a/div[@class="info"]'):
            date = self.parse_date(event)
            event_info = self.parse_event(event)
            price = self.parse_price(event)

            yield {
                "venue": self.name,
                "date": date,
                "name": event_info,
                "price": price,
            }


if __name__ == '__main__':
    aanivalli = Aanivalli()
    r = fetcher.retry_request(http.HTTPMethod.GET, aanivalli.url)

    for e in aanivalli.parse_events(r.content):
        for k, v in e.items():
            print(f"{k:>10s}: {v}")
        print()
