# -*- coding: utf-8 -*-

import re

from lxml import html

from venues.abstract_venue import AbstractVenue


class Tavastia(AbstractVenue):
    def __init__(self):
        super().__init__()
        self.url = "http://www.tavastiaklubi.fi"
        self.name = "Tavastia"
        self.city = "Helsinki"
        self.country = "Finland"

        # Parsing patterns
        self.datepat = re.compile("\d+\.\d+.\d+")

    def parse_price(self, tag):
        prices = tag.xpath('./a[@class="event-details-col"]/' + \
                           'p[@class="event-details"]' + \
                           '/span[@class="event-priceinfo"]')
        prices = [i.text_content() for i in prices \
                  if i.text_content() != ' ']

        return "/".join(prices)

    def parse_date(self, tag: html.HtmlElement) -> str:
        datetmp = ""

        if tag is None or len(tag) == 0:
            return ""

        datetmp = "".join(tag.xpath('./a[@class="event-date-col"]/span/text()'))

        day, month, year = datetmp.split(".")
        return "%s-%.2d-%.2d" % (int(year), int(month), int(day))

    def parse_event(self, tag: html.HtmlElement):
        date = self.parse_date(tag)
        event = tag.xpath('./a[@class="event-details-col"]/h2/text()')
        event = " ".join(event).replace("\n", "")
        event = re.sub("\s+", " ", event)
        event = event.lstrip(" ").rstrip(" ")

        price = self.parse_price(tag)

        return {"venue": self.get_venue_name(),
                "date": date,
                "name": event,
                "price": price}

    def parse_events(self, data: bytes):
        doc = html.fromstring(data)

        for tag in doc.xpath('//div[starts-with(@class, "event-content")]' + \
                             '/*/div[@class="event-row"]'):
            yield self.parse_event(tag)


if __name__ == '__main__':
    import requests

    d = Tavastia()
    r = requests.get(d.url)

    for i in d.parse_events(r.content):
        for k, v in i.items():
            print(f"{k:>10s}: {v}")
        print()
