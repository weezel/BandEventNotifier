#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re

import lxml.html

from venues.abstract_venue import AbstractVenue


class Korjaamo(AbstractVenue):
    def __init__(self):
        super().__init__()
        self.url = "https://korjaamo.fi/tapahtumat/"
        self.name = "Korjaamo"
        self.city = "Helsinki"
        self.country = "Finland"

        # Parsing patterns
        self.datepat = re.compile("[0-9.]{1,2}\\.[0-9]{1,2}\\.[0-9]{4}")

    def parse_date(self, tag: lxml.html.HtmlElement) -> str:
        pvm_tag = "".join(tag.xpath('.//div[@class="gt-date"]/span/text()'))
        if (parsed_pvm := self.datepat.search(pvm_tag)) is not None:
            day, month, year = parsed_pvm.group().split(".")
            day = int(day)
            month = int(month)
            year = int(year)
            return f"{year:04d}-{month:02d}-{day:02d}"

        return ""

    def parse_event(self, tag: lxml.html.HtmlElement) -> str:
        info_tag = "".join(tag.xpath('.//div[@class="gt-title"]/a/text()'))
        info_tag = re.sub("\\s+", " ", info_tag).lstrip(" ").rstrip(" ")
        return info_tag

    def parse_price(self, tag: lxml.html.HtmlElement) -> str:
        price_tag = "".join(tag.xpath('.//div[@class="gt-price"]/text()'))
        if price_tag == "":
            return "0€"
        price_tag = price_tag.rstrip("€")
        prices = price_tag.split("/")
        prices = [i.lstrip(" ").rstrip(" ") for i in prices]
        return "€/".join(prices).strip(" ") + "€"

    def parse_events(self, data: bytes):
        doc = lxml.html.fromstring(data)

        for event in doc.xpath('//div[@class="gt-col"]'):
            date = self.parse_date(event)
            event_info = self.parse_event(event)
            price = self.parse_price(event)

            yield {"venue": self.get_venue_name(),
                   "date": date,
                   "name": event_info,
                   "price": price}


if __name__ == '__main__':
    import requests

    korjaamo = Korjaamo()
    r = requests.get(korjaamo.url)

    for e in korjaamo.parse_events(r.content):
        for k, v in e.items():
            print(f"{k:>10s}: {v}")
        print()
