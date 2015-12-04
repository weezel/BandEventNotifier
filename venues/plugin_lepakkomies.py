#!/usr/bin/env python
# -*- coding: utf-8 -*-

import lxml.html

import re
import time


class PluginParseError(Exception): pass

class Lepakkomies(object):
    def __init__(self):
        # XXX Apparently they have a Facebook page and then Meteli.
        # Let's rely on the latter one.
        self.url = "http://www.meteli.net/lepakkomies"
        self.name = "Lepakkomies"
        self.city = "Helsinki"
        self.country = "Finland"

        # Parsing patterns
        self.monetaryp = re.compile("[0-9]+")

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
        return { u"name" : self.name, \
                 u"city" : self.city, \
                 u"country" : self.country }

    def parsePrice(self, line):
        tmp = re.search(self.monetaryp, line)
        if tmp:
            price = tmp.group()
        return u"0" if not tmp else u"%s€" % price

    def parseDate(self, tag):
        month_now = time.strftime("%m")
        year = int(time.strftime("%Y"))

        if len(tag) == 0:
            return u""

        day, month = tag.rstrip(".").split(".")
        # Are we on the new year already?
        if int(month) < int(month_now):
            year += 1

        return "%.4d-%.2d-%.2d" % (int(year), int(month), int(day))

    def parseEvent(self, tag):
        date = u""
        artist = u""
        price = u""

        datedata = " ".join(tag.xpath('.//span[contains(@class, ' + \
                             '"event-date")]/span/text()'))
        date = self.parseDate(datedata)
        artist = " ".join(tag.xpath('.//span[contains(@class, ' + \
                '"event-info")]/h2/text()'))
        price = " ".join(tag.xpath('.//span[contains(@class, ' + \
                '"price")]/text()'))

        return { u"venue" : self.getVenueName(),  \
                 u"date" : date,                  \
                 u"name" : "%s" % (artist),       \
                 u"price" : self.parsePrice(price) }

    def parseEvents(self, data):
        doc = lxml.html.fromstring(data)
        eventtags = doc.xpath('//div[@class="event-list"]')

        for et in eventtags:
            yield self.parseEvent(et)

if __name__ == '__main__':
    import requests

    k = Lepakkomies()
    r = requests.get(k.url)

    for e in k.parseEvents(r.content):
        for k, v in e.iteritems():
            print "%-10s: %s" % (k, v)
        print

