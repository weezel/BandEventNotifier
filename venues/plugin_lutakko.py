#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import lxml.html

import re
import time

from venues.abstract_venue import AbstractVenue


class PluginParseError(Exception): pass


class Lutakko(AbstractVenue):
    def __init__(self):
        super().__init__()
        self.url = "http://www.jelmu.net/"
        self.name = "Lutakko"
        self.city = "Jyväskylä"
        self.country = "Finland"

        # Parsing patterns
        self.datepat = re.compile("[0-9.]+")

    def parse_price(self, t):
        tag = " ".join(t.xpath('./div[@role="tickets"]/div/a/strong/text()'))

        return "0" if len(tag) == 0 else "%s" % tag

    def parse_date(self, t):
        month_now = time.strftime("%m")
        year = int(time.strftime("%Y"))
        date = ""

        tag = " ".join(t.xpath('./div[@class="badges"]' +
                               '/div[@class="date"]' +
                               '/span/text()'))
        splt = tag.split(" - ")
        slen = len(splt)
        if slen == 1:
            date = " ".join(re.findall(self.datepat, tag))
        # We only care about the starting date
        elif slen > 1:
            date = " ".join(re.findall(self.datepat, tag)[0])
        date = date.rstrip(".")  # FIXME

        day, month = date.split(".")

        # Are we on the new year already?
        if int(month) < int(month_now):
            year += 1

        return "%.4d-%.2d-%.2d" % (int(year), int(month), int(day))

    def parse_event(self, tag):
        date = self.parse_date(tag)
        title = tag.xpath('./a')[0].text_content()
        desc = tag.xpath('./p')[0].text_content()
        price = self.parse_price(tag)

        name = f"{title} {desc}"
        name = re.sub("\s+", " ", name).lstrip(" ").rstrip(" ")

        return {
            "venue": self.get_venue_name(),
            "date": date,
            "name": name,
            "price": price
        }

    def parse_events(self, data: str):
        doc = lxml.html.fromstring(data)

        for event in doc.xpath('//ul[@role="upcoming-events"]/li'):
            yield self.parse_event(event)


if __name__ == '__main__':
    import requests

    l = Lutakko()
    r = requests.get(l.url)

    for e in l.parse_events(r.content):
        for k, v in e.items():
            print(f"{k:>10s}: {v}")
        print()
