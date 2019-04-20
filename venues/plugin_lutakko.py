#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import lxml.html

import re
import time


class PluginParseError(Exception): pass

class Lutakko(object):
    def __init__(self):
        self.url = "http://www.jelmu.net/"
        self.name = "Lutakko"
        self.city = "Jyväskylä"
        self.country = "Finland"

        # Parsing patterns
        self.datepat = re.compile("[0-9.]+")

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
        tag = " ".join(t.xpath('./div[@role="tickets"]/div/a/strong/text()'))

        return "0" if len(tag) == 0 else "%s" % tag

    def parseDate(self, t):
        month_now = time.strftime("%m")
        year = int(time.strftime("%Y"))

        tag = " ".join(t.xpath('./div[@class="badges"]'  + \
                               '/div[@class="date"]'     + \
                               '/span/text()'))
        splt = tag.split(" - ")
        slen = len(splt)
        if slen == 1:
            date = " ".join(re.findall(self.datepat, tag))
        # We only care about the starting date
        elif slen > 1:
            date = " ".join(re.findall(self.datepat, tag))
            date = re.search(self.datepat, tag)
            if date:
                date = date.group()
            else:
                return ""
        date = date.rstrip(".")

        day, month = date.split(".")

        # Are we on the new year already?
        if int(month) < int(month_now):
            year += 1

        return "%.4d-%.2d-%.2d" % (int(year), int(month), int(day))

    def parseEvent(self, tag):
        date = ""
        title = ""
        desc = ""
        price = ""

        date = self.parseDate(tag)
        title = tag.xpath('./a')[0].text_content()
        desc = tag.xpath('./p')[0].text_content()
        price = self.parsePrice(tag)

        name = "%s %s" % (title, desc)
        name = re.sub("\s+", " ", name).lstrip(" ").rstrip(" ")

        return { "venue" : self.getVenueName(), \
                 "date" : date,                 \
                 "name" : name,                 \
                 "price" : price }

    def parseEvents(self, data):
        doc = lxml.html.fromstring(data)

        for event in doc.xpath('//ul[@role="upcoming-events"]/li'):
            yield self.parseEvent(event)

if __name__ == '__main__':
    import requests

    l = Lutakko()
    r = requests.get(l.url)

    for e in l.parseEvents(r.content):
        for k, v in e.items():
            print(f"{k:>10s}: {v}")
        print

