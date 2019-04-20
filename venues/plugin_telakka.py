#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import lxml.html

import re
import time


class PluginParseError(Exception): pass

class Telakka(object):
    def __init__(self):
        self.url = "http://www.telakka.eu/ravintola/ohjelma"
        self.name = "Telakka"
        self.city = "Tampere"
        self.country = "Finland"

        # Parsing patterns
        self.datepat = re.compile("(Ma|Ti|Ke|To|Pe|La|Su) [0-9]+.[0-9]+.")
        self.datepat2 = re.compile("[0-9]+.[0-9]+.")
        self.monetary = re.compile("[0-9/]+[ ]?€")

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

    def parsePrice(self, tag):
        # FIXME Cannot parse why this is not working yet.
        price = re.search(self.monetary, tag)
        if price:
            price = re.search("[0-9/]+", price.group)
        return "0" if not price else "%s€" % price

    def parseDate(self, tag):
        month_now = int(time.strftime("%m"))
        year = int(time.strftime("%Y"))

        date = re.search(self.datepat2, tag)
        if date == None:
            return ""

        day, month = date.group().rstrip(".").split(".")

         # Are we on the new year already?
        if int(month) < month_now:
            year += 1

        return "%.4d-%.2d-%.2d" % (int(year), int(month), int(day))

    def parseEvent(self, tag):
        date = ""
        price = ""
        title = ""

        date = self.parseDate(tag)
        title = tag.split(".", 2)
        if len(title) >= 3:
            title = title[2]
            title = re.sub("\s+", " ", title).lstrip(" ").rstrip(" ")
        price = self.parsePrice(title)

        return { "venue" : self.getVenueName(), \
                 "date" : date,                 \
                 "name" : "%s" % (title),       \
                 "price" : price }

    def parseEvents(self, data):
        doc = lxml.html.fromstring(data)

        for et in doc.xpath('//td[@class="main"]/table/tr'):
            isEvent = " ".join(et.xpath('./td[starts-with(@class, ' + \
                      '"item")]/text()'))

            if re.search(self.datepat, isEvent):
                yield self.parseEvent(isEvent)

if __name__ == '__main__':
    import requests

    p = Telakka()
    r = requests.get(p.url)

    for e in p.parseEvents(r.content):
        for k, v in e.items():
            print(f"{k:>10s}: {v}")
        print

