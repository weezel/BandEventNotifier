# -*- coding: utf-8 -*-

import re
import time

import lxml.html

from venues.abstract_venue import AbstractVenue


class Tavastia(AbstractVenue):
    def __init__(self):
        super().__init__()
        self.url = "https://tavastiaklubi.fi/?show_all=1"
        self.name = "Tavastia"
        self.city = "Helsinki"
        self.country = "Finland"

        # Parsing patterns
        self.datepat = re.compile("[0-9]+\\.[0-9]+\\.")

    def parse_price(self, tag):
        prices = "".join(tag.xpath('./div[@class="details"]/div[@class="info"]//div[@class="tickets"]/text()'))
        prices = prices.replace("\n", " ")
        prices = prices.replace("Liput ", "")
        prices = re.sub("\\s+", "", prices)

        return prices

    def parse_date(self, tag: lxml.html.HtmlElement) -> str:
        year = int(time.strftime("%Y"))
        month_now = int(time.strftime("%m"))
        tmp = "".join(tag.xpath('./div[@class="details"]/div[@class="date"]/text()'))
        if date_found := re.search(self.datepat, tmp):
            day, month = date_found.group().split(".")[0:2]
            if int(month) < month_now:
                year += 1
            return f"{year:04d}-{int(month):02d}-{int(day):02d}"

        return ""

    def parse_event(self, tag: lxml.html.HtmlElement):
        date = self.parse_date(tag)
        event = tag.xpath('./h2/text()')
        event = " ".join(event).replace("\n", "")
        event = re.sub("\\s+", " ", event)
        event = event.lstrip(" ").rstrip(" ")

        price = self.parse_price(tag)

        return {
            "venue": self.get_venue_name(),
            "date": date,
            "name": event,
            "price": price,
        }

    def parse_events(self, data: bytes):
        doc = lxml.html.fromstring(data)

        for tag in doc.xpath('//div[@class="tiketti-list"]/a'):
            yield self.parse_event(tag)


if __name__ == '__main__':
    import requests

    d = Tavastia()
    r = requests.get(d.url)

    for i in d.parse_events(r.content):
        for k, v in i.items():
            print(f"{k:>10s}: {v}")
        print()
