#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import http
import re
from typing import Any, Dict, Generator

import lxml.html
import requests

import fetcher
from venues.abstract_venue import AbstractVenue


class Tamperetalo(AbstractVenue):
    def __init__(self):
        super().__init__()
        self.url = "https://www.tampere-talo.fi/wp-admin/admin-ajax.php?action=em_event_feed&per_page=14&" + \
                   "page={page}&genres[]=468&genres[]=460&genres[]=478&genres[]=53&genres[]=554&" + \
                   "layout[]=list"
        self.name = "Tampere-Talo"
        self.city = "Tampere"
        self.country = "Finland"

        # Parsing patterns
        self.datepat = re.compile("[0-9]{1,2}\\.[0-9]{1,2}\\.[0-9]{4}")
        self.price_pat = r"[0-9]{1,2}€?"

    def parse_events(self, data: bytes) -> Generator[Dict[str, Any], None, None]:
        doc = lxml.html.fromstring(data)

        data = list()
        for i in range(1, 6):
            uu = self.url.format(page=str(i))
            req = requests.get(uu)
            req.raise_for_status()
            data.append(req.json())

        for events in data:
            for event in events:
                year, month, day = event["date"].split(" ")[0].split("-")
                yield {
                    "venue": self.name,
                    "date": f"{int(year):04d}-{int(month):02d}-{int(day):02d}",
                    "name": event["title"],
                    "price": "€",
                }


if __name__ == '__main__':
    tamperetalo = Tamperetalo()
    r = fetcher.retry_request(http.HTTPMethod.GET, tamperetalo.url)

    for e in tamperetalo.parse_events(r.content):
        for k, v in e.items():
            print(f"{k:>10s}: {v}")
        print()
