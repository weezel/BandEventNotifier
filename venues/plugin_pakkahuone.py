#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import http
import re
from typing import Any, Dict, Generator

import lxml.html

import fetcher
from venues.abstract_venue import AbstractVenue


class Pakkahuone(AbstractVenue):
    def __init__(self):
        super().__init__()
        self.url = "http://www.tullikamari.net/fi/tapahtumat"
        self.name = "Pakkahuone"
        self.city = "Tampere"
        self.country = "Finland"
        self.price_pat = r"[0-9,.]€"

    def parse_artists(self, tag: lxml.html.HtmlElement) -> str:
        title = " ".join(tag.xpath('.//h2[contains(@class, "event-artist")]/text()'))
        return re.sub(r"\s+", " ", title)

    def get_price(self, tag: lxml.html.HtmlElement) -> str:
        price_tags = " ".join(tag.xpath('./ul[@class="event-feed-item__info"]/li/text()'))
        prices = re.findall(self.price_pat, price_tags)
        if len(prices) == 0:
            return "0€"
        return "/".join(prices)

    def parse_events(self, data: bytes) -> Generator[Dict[str, Any], None, None]:
        doc = lxml.html.fromstring(data)
        events = doc.xpath('//div[contains(@class, "event-feed")]//div[@class="event-feed-item__content"]')
        for event in events:
            event_venue = " ".join(event.xpath('.//li[@class="event-venue"]/text()'))
            if "pakkahuone" not in event_venue.lower():
                continue

            date = "".join(event.xpath('.//time/text()'))
            if date.count("/") != 2:
                continue
            day, month, year = date.split("/")
            title = self.parse_artists(event)
            prices = self.get_price(event)
            yield {
                "venue": self.get_venue_name(),
                "date": "{:04d}-{:02d}-{:02d}".format(int(year), int(month), int(day)),
                "name": title,
                "price": prices,
            }


if __name__ == '__main__':
    pakkahuone = Pakkahuone()
    r = fetcher.retry_request(http.HTTPMethod.GET, pakkahuone.url)

    for e in pakkahuone.parse_events(r.content):
        for k, v in e.items():
            print(f"{k:>10s}: {v}")
        print()
