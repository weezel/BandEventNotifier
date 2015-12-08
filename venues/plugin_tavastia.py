# -*- coding: utf-8 -*-

from lxml import html

import time
import re

class PluginParseError(Exception): pass

class Tavastia(object):
    def __init__(self):
        self.url = "http://www.tavastiaklubi.fi/tapahtumat"
        self.name = "Tavastia"
        self.city = "Helsinki"
        self.country = "Finland"
        self.parseddata = None

        # Parsing patterns
        self.datepat = re.compile("\d+\.\d+.")
        self.monetarypattern = re.compile(u"[0-9.,]+ ?€")

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
        prices = re.findall(self.monetarypattern, line)
        if len(prices) < 1:
            return u"0"
        prices = map(lambda x: x.replace(" ", "").replace(",", "."), prices)

        return "/".join(prices)

    def parseDate(self, tag):
        month_now = time.strftime("%m")
        year = int(time.strftime("%Y"))
        date = u""
        datetmp = u""

        if len(tag) == 0:
            return u""

        datetmp = tag.text_content()
        parsedate = re.search(self.datepat, datetmp)
        if parsedate:
            date = parsedate.group()
            day, month = date.rstrip(".").split(".")

            # Are we on the new year already?
            if int(month) < int(month_now):
                year += 1
            return "%s-%.2d-%.2d" % (int(year), int(month), int(day))
        return u""

    def parseEvent(self, tag):
        date = u""
        event = u""
        price = u""

        tmp = tag.xpath('.//td[@class="event-listing-td"]')

        if len(tmp) < 2:
            raise PluginParseError("Error while parsing %s" % self.name)

        date = self.parseDate(tmp[0])
        event = tmp[1].text_content().replace("\n", " ").lstrip(" ").rstrip(" ")
        event = unicode(re.sub("\s+", " ", event))

        price = self.parsePrice(event)

        return { u"venue" : self.getVenueName(), \
                 u"date" : date,                 \
                 u"name" : event,                \
                 u"price" : price }


    def parseEvents(self, data):
        doc = html.fromstring(data)

        for tag in doc.xpath('//div[starts-with(@class, "event-listing-")]'):
            yield self.parseEvent(tag)

if __name__ == '__main__':
    import requests

    d = Tavastia()
    r = requests.get(d.url)
    daa = d.parseEvents(r.content)

    for i in daa:
        for k, v in i.iteritems():
            print "%-10s: %s" % (k, v)
        print

