#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import datetime
import http
import re
from typing import Any, Dict, Generator

import lxml.html

import fetcher
from venues.abstract_venue import AbstractVenue


class Mustakynnys(AbstractVenue):
    def __init__(self):
        super().__init__()
        self.url = "http://mustakynnys.com/"
        self.name = "Mustakynnys"
        self.city = "Jyväskylä"
        self.country = "Finland"

    def parse_date(self, tag: lxml.html.HtmlElement) -> str:
        pvm = " ".join(tag.xpath('.//div[@id="pvm"]/text()')).split(" ")
        if len(pvm) < 2:
            return ""
        day, month = pvm[1].rstrip(".").split(".")
        year = datetime.datetime.now().year
        return f"{int(year):04d}-{int(month):02d}-{int(day):02d}"

    def parse_event(self, tag: lxml.html.HtmlElement) -> str:
        doc = " ".join(tag.xpath('.//div[@id="keikannimi"]/strong/text()'))
        doc = re.sub(r"\s+", " ", doc).replace("\n", "")
        return doc

    def parse_events(self, data: bytes) -> Generator[Dict[str, Any], None, None]:
        doc = lxml.html.fromstring(data)

        for event in doc.xpath('//div[@id="keikka"]'):
            date = self.parse_date(event)
            tmp = " ".join(event.xpath('.//div[@id="keikannimi"]/a/text()'))
            price = self.parse_price(tmp)
            name = self.parse_event(event)

            yield {
                "venue": self.name,
                "date": date,
                "name": name,
                "price": price,
            }


if __name__ == '__main__':
    mustakynnys = Mustakynnys()
    r = fetcher.retry_request(http.HTTPMethod.GET, mustakynnys.url)

    for e in mustakynnys.parse_events(r.content):
        for k, v in e.items():
            print(f"{k:>10s}: {v}")
        print()
