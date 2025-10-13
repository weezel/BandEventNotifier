#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import http
import re
from typing import Any, Dict, Generator

import lxml.html

import fetcher
from venues.abstract_venue import AbstractVenue


class Kotelo(AbstractVenue):
    def __init__(self):
        super().__init__()
        self.url = "https://www.barkotelo.fi/Keikat/"
        self.name = "Kotelo"
        self.city = "Tampere"
        self.country = "Finland"

        # Parsing patterns
        self.datepat = re.compile("[0-9]{1,2}\\.[0-9]{1,2}\\.[0-9]{4}")
        self.price_pat = r"[0-9]{1,2}€?"

    def parse_date(self, tag: lxml.html.HtmlElement) -> str:
        try:
            pvm_tag = "".join(tag.xpath('.//h4[1]//text()'))
            if (parsed_pvm := self.datepat.search(pvm_tag)) is not None:
                day, month, year = parsed_pvm.group().split(".")
                day = int(day)
                month = int(month)
                year = int(year)
                return f"{year:04d}-{month:02d}-{day:02d}"
        except e:
            raise e

        return ""

    def parse_event(self, tag: lxml.html.HtmlElement) -> str:
        info_tag = ", ".join(tag.xpath('.//h4[position()>1 and following-sibling::h4[last()-2]]//text()'))
        info_tag = re.sub(r"\s+", " ", info_tag).lstrip(" ").rstrip(" ")
        info_tag = info_tag.replace("w/", "")
        info_tag = info_tag.lower().title()
        return info_tag

    def parse_price(self, tag: lxml.html.HtmlElement) -> str:
        price_tag = "".join(tag.xpath('.//h4[last()-1]/text()'))
        price_tag = price_tag.replace("€", "")
        prices = re.findall(self.price_pat, price_tag)
        return "/".join([f"{p}€" for p in prices])

    def parse_events(self, data: bytes) -> Generator[Dict[str, Any], None, None]:
        doc = lxml.html.fromstring(data)

        pat = '//div[contains(@class, "wb_content wb-layout-vertical")]' + \
              '/div[contains(@class, "wb_element wb-layout-element")]' + \
              '//div[contains(@class, "wb_element wb_text_element")]'
        for event in doc.xpath(pat):
            date = self.parse_date(event)
            if date == "":
                continue
            event_info = self.parse_event(event)
            if event_info == "":
                continue
            price = self.parse_price(event)

            yield {
                "venue": self.name,
                "date": date,
                "name": event_info,
                "price": price,
            }


if __name__ == '__main__':
    korjaamo = Kotelo()
    r = fetcher.retry_request(http.HTTPMethod.GET, korjaamo.url)

    for e in korjaamo.parse_events(r.content):
        for k, v in e.items():
            print(f"{k:>10s}: {v}")
        print()
