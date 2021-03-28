#!/usr/bin/env python3
import re
from typing import Any, Dict, Generator

import lxml.html

from venues.abstract_venue import AbstractVenue


class PluginParseError(Exception):
    pass


class Yotalo(AbstractVenue):
    def __init__(self):
        super().__init__()
        self.url = "https://yo-talo.fi/ohjelma/"
        self.name = "Yo-talo"
        self.city = "Tampere"
        self.country = "Finland"

    def normalize_string(self, s: str):
        rm_newlines = s.replace("\n", " ")
        rm_spaces = re.sub("\s+", " ", rm_newlines)
        rm_left_padding = re.sub("^\s+", "", rm_spaces)
        rm_right_padding = re.sub("\s+$", "", rm_left_padding)
        return rm_right_padding

    def month_to_number(self, month: str) -> int:
        if month == "tammi":
            return 1
        elif month == "helmi":
            return 2
        elif month == "maalis":
            return 3
        elif month == "huhti":
            return 4
        elif month == "touko":
            return 5
        elif month == "kesä":
            return 6
        elif month == "heinä":
            return 7
        elif month == "elo":
            return 8
        elif month == "syys":
            return 9
        elif month == "loka":
            return 10
        elif month == "marras":
            return 11
        elif month == "joulu":
            return 12

        raise ValueError(f"Month mapping for '{month}' not implemented")

    def parse_date(self, tag: lxml.html.HtmlElement) -> str:
        day = "".join(tag[0].xpath('./div[@class="event-day"]/text()'))
        day = int(day)
        month = "".join(tag[0].xpath('./div[@class="event-month"]/text()'))
        month = self.month_to_number(month)
        year = "".join(tag[0].xpath('./div[@class="event-year"]/text()'))
        year = int(year)
        return f"{year:04d}-{month:02d}-{day:02d}"

    def parse_info(self, event: lxml.html.HtmlElement) -> str:
        title = "".join(event[0].xpath('./div[@class="event-title"]/h3/text()'))
        title = self.normalize_string(title)
        description = "".join(event[0].xpath('./div[@class="event-details"]')[0].text_content())
        description = self.normalize_string(description)

        return f"{title}: {description}"

    def parse_event(self, event: lxml.html.HtmlElement) -> Dict[str, Any]:
        date = self.parse_date(event.xpath('./div[@class="event-date"]/div[@class="start-date"]'))
        event_name = self.parse_info(event.xpath('./div[contains(@class, "event-info single-day")]'))
        price = self.parse_price(event_name)

        return {"venue": self.get_venue_name(),
                "date": date,
                "name": event_name,
                "price": price}

    def parse_events(self, data: bytes) -> Generator[Dict[str, Any], None, None]:
        doc = lxml.html.fromstring(data)

        for item in doc.xpath('/html/body//div[@class="event-list"]/ul[@class="event-list-view"]'
                              '/li[contains(@class, "event live")]'):
            yield self.parse_event(item)


if __name__ == '__main__':
    import requests

    y = Yotalo()
    r = requests.get(y.url)

    for e in y.parse_events(r.content):
        for k, v in e.items():
            print(f"{k:>10s}: {v}")
        print()
