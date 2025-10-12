#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import http
import re
import time
from datetime import datetime
from typing import Any, Dict, Generator

import lxml.html

import fetcher
from venues.abstract_venue import AbstractVenue


class Lutakko(AbstractVenue):
    def __init__(self):
        super().__init__()
        self.url = "http://www.jelmu.net/"
        self.name = "Lutakko"
        self.city = "Jyväskylä"
        self.country = "Finland"

        # Parsing patterns
        self.datepat = re.compile("[0-9.]+")

    def parse_price(self, tag: lxml.html.HtmlElement) -> str:
        prices = tag.xpath('string(.//span[@class="price"]/span/bdi)')
        return prices

    def parse_date(self, tag: lxml.html.HtmlElement) -> str:
        date = " ".join(tag.xpath('.//span[@class="date"]/text()'))

        day, month = date.rstrip(".").split(".")

        year = datetime.now().year
        # Are we on the new year already?
        month_now = time.strftime("%m")
        if int(month) < int(month_now):
            year += 1
        return "{:04d}-{:02d}-{:02d}".format(int(year), int(month), int(day))

    def parse_events(self, data: str) -> Generator[Dict[str, Any], None, None]:
        doc = lxml.html.fromstring(data)

        for event in doc.xpath('//a[contains(@class, "woocommerce-LoopProduct-link")]'):
            date = self.parse_date(event)
            title = event.xpath('string(.//h2[contains(@class, "woocommerce-loop-product__title")])').strip()
            price = self.parse_price(event)

            yield {
                "venue": self.name,
                "city": self.city,
                "date": date,
                "name": title,
                "price": price
            }


if __name__ == '__main__':
    lutakko = Lutakko()
    r = fetcher.retry_request(http.HTTPMethod.GET, lutakko.url)

    for e in lutakko.parse_events(r.content):
        for k, v in e.items():
            print(f"{k:>10s}: {v}")
        print()
