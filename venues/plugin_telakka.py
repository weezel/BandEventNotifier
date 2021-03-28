#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import datetime
import re
from typing import Any, Dict, Generator

import lxml.html

from venues.abstract_venue import AbstractVenue


class Telakka(AbstractVenue):
    def __init__(self):
        super().__init__()
        self.url = "http://www.telakka.eu/ravintola/ohjelma"
        self.name = "Telakka"
        self.city = "Tampere"
        self.country = "Finland"

        # Parsing patterns
        self.pat_date = re.compile("[0-9]+.[0-9]+.")

    def parse_date(self, elem: lxml.html.HtmlElement):
        date_now = datetime.datetime.now()

        try:
            parsed = " ".join(elem.xpath('./strong/text()'))
            # TODO Use walrus operator
            # FIXME year swap
            if re.search(self.pat_date, parsed):
                parsed_date = re.search(self.pat_date, parsed).group()
                parsed_date2 = f'{parsed_date}{date_now.year}'
                return datetime.datetime.strptime(parsed_date2, "%d.%m.%Y")
        except Exception:
            return ""

    def parse_events(self, data: bytes) \
            -> Generator[Dict[str, Any], None, None]:
        doc = lxml.html.fromstring(data)

        for et in doc.xpath('//div[@class="entry-content"]/p/span[@style="color: #ff6600;"]'):
            event_date = self.parse_date(et)
            if event_date is None:
                continue

            tmp = "".join(et.xpath("../text()")).replace("\r\n", " ")
            event = re.sub("\s+", " ", tmp).strip()
            price = self.parse_price(event)

            tmp = "".join(et.xpath('../strong/text()')).replace("\r\n", " ")
            has_title = re.sub("\s+", " ", tmp).strip()

            if has_title != "":
                ename = "{}: {}".format(has_title, event)
            else:
                ename = event

            yield {"venue": self.get_venue_name(),
                   "date": event_date,
                   "name": ename,
                   "price": price}


if __name__ == '__main__':
    import requests

    p = Telakka()
    r = requests.get(p.url)

    for e in p.parse_events(r.content):
        for k, v in e.items():
            print(f"{k:>10s}: {v}")
        print()
