#!/usr/bin/env python
# -*- coding: utf-8 -*-

import lxml.html

import re
import time


class PluginParseError(Exception): pass

class Kuudeslinja(object):
    def __init__(self):
        self.url = "http://www.kuudeslinja.com/"
        self.name = "Kuudeslinja"
        self.city = "Helsinki"
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
        return { u"name" : self.name, \
                 u"city" : self.city, \
                 u"country" : self.country }

    def parsePrice(self, tag):
        # TODO Lacking implementation
        return u"0"

    def parseDate(self, tag):
        month_now = time.strftime("%m")
        year = int(time.strftime("%Y"))
        ttag = " ".join(tag)
        d = re.sub("\s+", " ", ttag)
        d = d.rstrip(" ")
        d = d.split(" ")

        if len(d) != 2:
            return u""

        day, month = d[1].rstrip(".").split(".")
        # Are we on the new year already?
        if int(month) < int(month_now):
            year += 1

        return "%.4d-%.2d-%.2d" % (int(year), int(month), int(day))

    def parseEvent(self, tag):
        date = u""
        title = u""
        event = u""
        price = u""

        date = self.parseDate(tag.xpath('./span[@class="pvm"]/text()'))
        event = " ".join(tag.xpath('./span[@class="title"]/text()'))
        event = unicode(event)

        return { u"venue" : self.getVenueName(), \
                 u"date" : date,                 \
                 u"name" : event,                \
                 u"price" : price }

    def parseEvents(self, data):
        doc = lxml.html.fromstring(data)

        for event in doc.xpath('/html/body/div/div/div/a'):
            yield self.parseEvent(event)

if __name__ == '__main__':
    import requests

    k = Kuudeslinja()
    r = requests.get(k.url)

    for e in k.parseEvents(r.content):
        for k, v in e.iteritems():
            print "%-10s: %s" % (k, v)
        print

