#!/usr/bin/env python
# -*- coding: utf-8 -*-

import lxml.html

import re
import time


class PluginParseError(Exception): pass

class Oharas(object):
    def __init__(self):
        self.url = "https://www.gastropub.net/oharas/keikkakalenteri/"
        self.name = "O'Hara's"
        self.city = "Tampere"
        self.country = "Finland"

        # Parsing patterns
        self.datepat = re.compile("^[0-9]{,2}.[0-9]{,2}. ")

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
        return u"0" if line == "-" else u"%s€" % line

    def parseDate(self, tag):
        month_now = time.strftime("%m")
        year = int(time.strftime("%Y"))

        if tag == None:
            return u""

        day, month = tag.group().rstrip(" .").split(".")
        # Are we on the new year already?
        if int(month) < int(month_now):
            year += 1

        return "%.4d-%.2d-%.2d" % (int(year), int(month), int(day))

    def parseEvent(self, tag):
        """
        Example format:
        04.12. LifeLine + Vaara
        """
        date = u""
        title = u""

        datedata = re.search(self.datepat, tag.text_content())
        date = self.parseDate(datedata)

        title = tag.text_content().split(" ", 1)
        if len(title) > 1:
            title = title[1]
        else:
            title = u""

        price = u"0"

        return { u"venue" : self.getVenueName(),  \
                 u"date" : date,                  \
                 u"name" : "%s" % (title),        \
                 u"price" : price }

    def parseEvents(self, data):
        doc = lxml.html.fromstring(data)
        eventtags = doc.xpath('//section[@id="main-content"]/p')

        for et in eventtags:
            parsed = self.parseEvent(et)
            if len(parsed["date"]) == 0:
                continue
            yield parsed

if __name__ == '__main__':
    import requests

    k = Oharas()
    r = requests.get(k.url)

    #with open("venues/oharas.html") as f:
    #    r = f.read()

    #for e in k.parseEvents(r):
    for e in k.parseEvents(r.content):
        for k, v in e.iteritems():
            print "%-10s: %s" % (k, v)
        print

