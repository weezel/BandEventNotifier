#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re

import lxml.html

from venues.abstract_venue import AbstractVenue


class PluginParseError(Exception):
    pass


class Olympia(AbstractVenue):
    def __init__(self):
        super().__init__()
        self.url = "http://olympiakortteli.fi/keikat/"
        self.name = "Olympia-kortteli"
        self.city = "Tampere"
        self.country = "Finland"

        # Parsing patterns
        self.datepat = re.compile("[0-9.]{1,2}\.[0-9]{1,2}\.[0-9]{4}")
        self.pricepat_monetary = re.compile("[0-9,]+.€")
        self.pricepat_plain = re.compile("[0-9,]+")

    def parse_price(self, info_tag: str) -> str:
        prices_with_mon = self.pricepat_monetary.findall(info_tag)
        prices = []
        for price in prices_with_mon:
            parsed_price = self.pricepat_plain.findall(price)
            if len(parsed_price) == 0:
                continue
            prices.append("".join(parsed_price))

        if len(prices) == 0:
            return "0€"
        elif len(prices) == 2:
            in_advance, from_door = prices[0], prices[1]
            return f"{in_advance}€/{from_door}€"
        return "{}€".format("".join(prices))

    def parse_date(self, tag: lxml.html.HtmlElement) -> str:
        pvm_tag = tag.xpath('./div[contains(@class, "pvm")]')[0].text_content()
        if (parsed_pvm := self.datepat.search(pvm_tag)) is not None:
            day, month, year = parsed_pvm.group().split(".")
            day = int(day)
            month = int(month)
            year = int(year)
            return f"{year:04d}-{month:02d}-{day:02d}"

        return ""

    def parse_event(self, tag: lxml.html.HtmlElement) -> str:
        info_tag = tag.xpath('./div[contains(@class, "infot")]')[0].text_content()
        info_tag = re.sub("\s+", " ", info_tag).lstrip(" ").rstrip(" ")
        return info_tag

    def parse_events(self, data: bytes):
        doc = lxml.html.fromstring(data)

        for event in doc.xpath('/html[@class="no-js"]/body//div[contains(@class, "keikka")]'):
            date = self.parse_date(event)
            event_info = self.parse_event(event)
            price = self.parse_price(event_info)

            yield {"venue": self.get_venue_name(),
                   "date": date,
                   "name": event_info,
                   "price": price}


if __name__ == '__main__':
    import requests

    olympia = Olympia()
    r = requests.get(olympia.url)

    for e in olympia.parse_events(r.content):
        for k, v in e.items():
            print(f"{k:>10s}: {v}")
        print()
