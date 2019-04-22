#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re

import lxml.html


class PluginParseError(Exception): pass

class Ontherocks(object):
    def __init__(self):
        self.url = "https://www.rocks.fi/tapahtumat/"
        self.name = "On The Rocks"
        self.city = "Helsinki"
        self.country = "Finland"

        # Parsing patterns
        self.datepat = re.compile("[0-9]{,2}.[0-9]{,2}.[0-9]{4}")
        self.pricepat = re.compile("[0-9,]+/[0-9,]+")

    def getVenueName(self):
        return self.name

    def getCity(self):
        return self.city

    def getCountry(self):
        return self.country

    def eventSQLentity(self):
        """
        This method is used to ensure venue exists in venue SQL table.
        """
        return { "name" : self.name, \
                 "city" : self.city, \
                 "country" : self.country }

    def parsePrice(self, parsed_price):
        if parsed_price is not None:
            price = re.search(self.pricepat, parsed_price)
            if price:
                return price.group()
        return "0"

    def parseDate(self, tag):
        date = re.search(self.datepat, tag)
        if date is None:
            return ""

        day, month, year = date.group().split(".")
        return "%.4d-%.2d-%.2d" % (int(year), int(month), int(day))

    def parseEvent(self, tag):
        """
        > artist
        parsed.xpath('//div[@class="entry-content"]/h1/a/text()')
        > date
        parsed.xpath('//div[@class="entry-content"]/span[contains(@class, "entry-details")]/span/text()')
        > ticket price:
        <div class="ticket-info"> / span
        """

        date = ""
        artist = ""
        desc = ""

        datedata = " ".join(tag.xpath('./div[@class="entry-content"]' + \
                '/span[contains(@class, "entry-details")]/span/text()'))
        date = self.parseDate(datedata)

        artist = " ".join(tag.xpath('./div[@class="entry-content"]' + \
                '/h1/a/text()'))
        artist = artist.strip()

        parsed_price = "".join(tag.xpath('./div[@class="ticket-info"]' + \
                '/span/text()'))
        price = self.parsePrice(parsed_price)

        return { "venue" : self.getVenueName(),  \
                 "date" : date,                   \
                 "name" : "%s" % (artist), \
                 "price" : f"{price}" }

    def parseEvents(self, data):
        doc = lxml.html.fromstring(data)
        eventtags = doc.xpath("//div[@class='tapahtuma-inner']")

        for et in eventtags:
            yield self.parseEvent(et)

if __name__ == '__main__':
    import requests

    k = OnTheRocks()
    r = requests.get(k.url)

    for e in k.parseEvents(r.content):
        for k, v in e.items():
            print(f"{k:>10s}: {v}")
        print()

