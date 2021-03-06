#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import lxml.html

import re
import time


class PluginParseError(Exception): pass

class Olympia(object):
    def __init__(self):
        self.url = "http://olympiakortteli.fi/keikat/"
        self.name = "Olympia-kortteli"
        self.city = "Tampere"
        self.country = "Finland"

        # Parsing patterns
        self.datepat = re.compile("[0-9.]+")
        self.monetary = re.compile("[0-9]+(\s+)?€")

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

    def parsePrice(self, t):
        # XXX Fix this
        return 0
        #tag = t.xpath('./div[2]/strong/text()')

        #foundprice = re.findall(self.monetary, " ".join(tag))

        #if foundprice is None:
        #    foundprice = ""

        #return "0" if len(foundprice) == 0 else "%s" % (foundprice[0])

    def parseDate(self, t):
        tag = t.xpath('./div[2]/text()')

        if tag:
            tag = " ".join(tag)
            tag = re.sub("\s+", " ", tag).lstrip(" ").rstrip(" ")

        founddate = re.search(self.datepat, tag)

        if founddate is None:
            return ""

        day, month, year = founddate.group().split(".")
        return "%.4d-%.2d-%.2d" % (int(year), int(month), int(day))

    def parseEvents(self, data):
        doc = lxml.html.fromstring(data)
        date = ""
        name = ""
        price = ""

        for event in doc.xpath('//div[contains(@class, "keikkalista")]/div'):
            name = "".join(event.xpath("./div/h3/text()"))
            name = re.sub("\s+", " ", name).lstrip(" ").rstrip(" ")
            date = self.parseDate(event)
            price = self.parsePrice(event)

            yield { "venue" : self.getVenueName(), \
                    "date" : date, \
                    "name" : name, \
                    "price" : price }

if __name__ == '__main__':
    import requests

    l = Olympia()
    r = requests.get(l.url)

    for e in l.parseEvents(r.content):
        for k, v in e.items():
            print(f"{k:>10s}: {v}")
        print

