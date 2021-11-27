#!/usr/bin/env python3
import re
from typing import Any, Dict, Generator

import lxml.html

from venues.abstract_venue import AbstractVenue


class Yotalo(AbstractVenue):
    def __init__(self):
        super().__init__()
        self.url = "https://yo-talo.fi/ohjelma/"
        self.name = "Yo-talo"
        self.city = "Tampere"
        self.country = "Finland"
        self.date_pat = re.compile("[0-9]{1,2}\\.[0-9]{1,2}\\.[0-9]{4}")

    def normalize_string(self, s: str):
        rm_newlines = s.replace("\n", " ")
        rm_spaces = re.sub("\\s+", " ", rm_newlines)
        rm_left_padding = re.sub("^\\s+", "", rm_spaces)
        rm_right_padding = re.sub("\\s+$", "", rm_left_padding)
        return rm_right_padding

    def parse_date(self, tag: lxml.html.HtmlElement) -> str:
        date_tag = "".join(tag.xpath('./*/div[contains(@class, "event-content")]/p[2]/text()'))
        if date_found := re.search(self.date_pat, date_tag):
            day, month, year = date_found.group().split(".")
            return f"{int(year):04d}-{int(month):02d}-{int(day):02d}"
        return "00-00-0000"

    def parse_price(self, tag: lxml.html.HtmlElement) -> str:
        price_elem = "".join(tag.xpath('./*/div[contains(@class, "event-content")]'
                                       '/p[contains(text(), "Ennakkoliput")]/text()'))
        prices_with_mon = self.pricepat_monetary.findall(price_elem)
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

    def parse_artists(self, tag: lxml.html.HtmlElement) -> str:
        title = "".join(tag.xpath('./*/div[@class="event-title"]/h3/text()'))
        title = self.normalize_string(title)
        info = "".join(tag.xpath('./*/div[@class="event-content"]/p[2]/strong/text()'))
        info = self.normalize_string(info)

        return f"{title}: {info}"

    def parse_events(self, data: bytes) -> Generator[Dict[str, Any], None, None]:
        doc = lxml.html.fromstring(data)

        for item in doc.xpath('//li[contains(@class, "event live")]'):
            date = self.parse_date(item)
            if date == "00-00-0000":
                continue
            event = self.parse_artists(item)
            price = self.parse_price(item)

            yield {
                "venue": self.get_venue_name(),
                "date": date,
                "name": event,
                "price": price
            }


if __name__ == '__main__':
    import requests

    y = Yotalo()
    r = requests.get(y.url)

    for e in y.parse_events(r.content):
        for k, v in e.items():
            print(f"{k:>10s}: {v}")
        print()
