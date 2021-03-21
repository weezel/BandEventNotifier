# -*- coding: utf-8 -*-
from typing import Any, Dict, Generator

import lxml.html

from venues.abstract_venue import AbstractVenue


class Vastavirta(AbstractVenue):
    def __init__(self):
        super().__init__()
        self.url = "http://vastavirta.net/fi/"
        self.name = "Vastavirta"
        self.city = "Tampere"
        self.country = "Finland"
        self.parseddata = None
        self.monthmap = {
            "Tammi": 1,
            "Helmi": 2,
            "Maalis": 3,
            "Huhti": 4,
            "Touko": 5,
            "Kesä": 6,
            "Heinä": 7,
            "Elo": 8,
            "Syys": 9,
            "Loka": 10,
            "Marras": 11,
            "Joulu": 12
        }

    def parse_price(self, tag: lxml.html.HtmlElement) -> str:
        parsedprice = tag.xpath('.//div[@class="event-details"]/*/text()')
        prices = " ".join(parsedprice)

        return f"{prices}" if prices else "0"

    def parse_date(self, tag: lxml.html.HtmlElement) -> str:
        day = tag.xpath('./*/div[@class="start-date"]/div[@class="event-day"]/text()')
        m = tag.xpath('./*/div[@class="start-date"]/div[@class="event-month"]/text()')
        year = tag.xpath('./*/div[@class="start-date"]/div[@class="event-year"]/text()')

        day = " ".join(day)
        month = " ".join(m).capitalize()
        year = " ".join(year)

        is_day_empty = day == ""
        is_month_empty = month == ""
        is_year_empty = year == ""
        if any([is_day_empty, is_month_empty, is_year_empty]):
            return ""

        month = self.monthmap[month]
        return "%.4d-%.2d-%.2d" % (int(year), int(month), int(day))

    def parse_event(self, event: lxml.html.HtmlElement) -> Dict[str, Any]:
        date = self.parse_date(event)
        etitle = " ".join(event.xpath('./*/div[@class="event-title"]/*/text()'))
        prices = self.parse_price(event)

        return {"venue": self.get_venue_name(),
                "date": date,
                "name": etitle,
                "price": prices}

    def parse_events(self, data) \
            -> Generator[Dict[str, Any], None, None]:
        doc = lxml.html.fromstring(data).getroottree().getroot()
        tags = doc.xpath('//div[@class="event-list"]/ul'
                         + '[@class="event-list-view"]'
                         + '/li[@class="event "]')
        tmp = ""

        for event in reversed(tags):
            parsed = self.parse_event(event)

            if parsed["date"] == "":
                tmp += ", " + parsed["name"]
            else:
                parsed["name"] += tmp
                yield parsed
                tmp = ""


if __name__ == '__main__':
    import requests

    v = Vastavirta()
    r = requests.get(v.url)

    # with open("venues/vastavirta.html") as f:
    #    r = f.read()

    for event in v.parse_events(r.content):
        for k, v in event.items():
            print(f"{k:>10s}: {v}")
        print()
