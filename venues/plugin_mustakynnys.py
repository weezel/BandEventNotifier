#!/usr/bin/env python
# -*- coding: utf-8 -*-

import lxml.html

import re
import time


class PluginParseError(Exception): pass

class Mustakynnys(object):
    def __init__(self):
        self.url = "http://mustakynnys.com/"
        self.name = "Mustakynnys"
        self.city = u"Jyväskylä"
        self.country = "Finland"

        # Parsing patterns
        self.datepat = re.compile("[0-9.]+")
        self.monetary = re.compile(u"[0-9]+(\s+)?€")

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

    def parsePrice(self, t):
        # TODO Broken, fix it
        tag = t.xpath('./text()')

        foundprice = re.search(self.monetary, " ".join(tag))

        #print "TAG: %s" % tag

        if foundprice is None:
            foundprice = ""

        return u"0" if len(foundprice) == 0 else u"%s" % foundprice.strip(" ")

    def parseDate(self, t):
        tag = t.xpath('./text()')

        founddate = re.search(self.datepat, " ".join(tag))

        if founddate is None:
            return ""

        day, month, year = founddate.group().split(".")
        return u"%.4d-%.2d-%.2d" % (int(year), int(month), int(day))

    def parseEvents(self, data):
        doc = lxml.html.fromstring(data)
        date = ""
        name = ""
        price = ""

        for event in reversed(doc.xpath('//div[@id="boxleft"]/p[@class="pvm" '
                                      + 'or @class="keikka"]')):
            # Price is also included under the pvm tag
            if event.get("class") == "pvm":
                date = self.parseDate(event)
                price = self.parsePrice(event)

                name = re.sub("\s+", " ", name).replace("\n", "")

                yield { u"venue" : self.getVenueName(), \
                        u"date" : date,                 \
                        u"name" : name,                 \
                        u"price" : price }
                name = u""
            elif event.get("class") == "keikka":
                name += " ".join(event.xpath('./a/text()'))

if __name__ == '__main__':
    import requests

    l = Mustakynnys()
    r = requests.get(l.url)

    for e in l.parseEvents(r.content):
        for k, v in e.iteritems():
            print "%-10s: %s" % (k, v)
        print

