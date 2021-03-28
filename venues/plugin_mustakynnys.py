#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
from typing import Any, Dict, Generator

import lxml.html

from venues.abstract_venue import AbstractVenue


class Mustakynnys(AbstractVenue):
    def __init__(self):
        super().__init__()
        self.url = "http://mustakynnys.com/"
        self.name = "Mustakynnys"
        self.city = "Jyväskylä"
        self.country = "Finland"

        # Parsing patterns
        self.datepat = re.compile("[0-9.]+")
        self.monetary = re.compile("[0-9]+(\s+)?€")

    def parse_date(self, t: lxml.html.HtmlElement) -> str:
        tag = t.xpath('./text()')

        founddate = re.search(self.datepat, " ".join(tag))

        if founddate is None:
            return ""

        day, month, year = founddate.group().split(".")
        return f"{year:04d}-{month:02d}-{day:02d}"

    def parse_events(self, data: bytes) \
            -> Generator[Dict[str, Any], None, None]:
        doc = lxml.html.fromstring(data)
        name = ""

        for event in reversed(doc.xpath('//div[@id="boxleft"]/p[@class="pvm" '
                                        'or @class="keikka"]')):
            # Price is also included under the pvm tag
            if event.get("class") == "pvm":
                date = self.parse_date(event)
                price = self.parse_price(event)

                name = re.sub("\s+", " ", name).replace("\n", "")

                yield {"venue": self.get_venue_name(),
                       "date": date,
                       "name": name,
                       "price": price}
                name = ""
            elif event.get("class") == "keikka":
                name += " ".join(event.xpath('./a/text()'))


if __name__ == '__main__':
    import requests

    l = Mustakynnys()
    r = requests.get(l.url)

    for e in l.parse_events(r.content):
        for k, v in e.items():
            print(f"{k:>10s}: {v}")
        print()
