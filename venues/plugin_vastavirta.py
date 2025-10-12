# -*- coding: utf-8 -*-
import http
import re
from datetime import datetime
from typing import Any, Dict, Generator

import lxml.html

import fetcher
from venues.abstract_venue import AbstractVenue


class Vastavirta(AbstractVenue):
    def __init__(self):
        super().__init__()
        self.url = "http://vastavirta.net/fi/"
        self.name = "Vastavirta"
        self.city = "Tampere"
        self.country = "Finland"
        self.monetary_pat = "[0-9]+"

    def parse_price(self, tag: lxml.html.HtmlElement) -> str:
        tickets = tag.xpath('./p/text()')
        for ticket in tickets:
            if "Liput:" in ticket:
                tickets = ticket
                break
            if "Ilmainen sisäänpääsy" in ticket:
                return "0€"

        if len(tickets) == "":
            return "0€"

        parsed = re.findall(self.monetary_pat, tickets)
        if len(parsed) == 2:
            return f"{parsed[0]}€ / {parsed[1]}€"

        return f"{parsed[0]}€"

    def parse_date(self, d: str) -> str:
        date = d.split(sep=" ")[0]
        parsed = datetime.strptime(date, "%d.%m.%Y")
        return "{:04d}-{:02d}-{:02d}".format(parsed.year, parsed.month, parsed.day)

    def parse_event(self, event: lxml.html.HtmlElement) -> Dict[str, Any]:
        date, etitle = " ".join(event.xpath('./h3[@class="vv-events-heading"]/text()')).split(sep=" - ", maxsplit=1)
        etitle = etitle.lstrip()
        date = self.parse_date(date)
        prices = self.parse_price(event)

        return {
            "venue": self.name,
            "city": self.city,
            "date": date,
            "name": etitle,
            "price": prices,
        }

    def parse_events(self, data: bytes) -> Generator[Dict[str, Any], None, None]:
        doc = lxml.html.fromstring(data).getroottree().getroot()
        events = doc.xpath('//div[@class="vv-custom-events"]')

        for event in events:
            parsed = self.parse_event(event)

            if parsed["date"] == "":
                continue

            yield parsed


if __name__ == '__main__':
    v = Vastavirta()
    r = fetcher.retry_request(http.HTTPMethod.GET, v.url)

    for event in v.parse_events(r.content):
        for k, v in event.items():
            print(f"{k:>10s}: {v}")
        print()
