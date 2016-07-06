# -*- coding: utf-8 -*-

from lxml import html

import time
import re

class PluginParseError(Exception): pass

class Tavastia(object):
    def __init__(self):
        self.url = "http://www.tavastiaklubi.fi"
        self.name = "Tavastia"
        self.city = "Helsinki"
        self.country = "Finland"
        self.parseddata = None

        # Parsing patterns
        self.datepat = re.compile("\d+\.\d+.\d+")

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
        price = tag.xpath('./a[@class="event-details-col"]/' + \
                          'p[@class="event-details"]' +        \
                          '/span[@class="event-priceinfo"]')
        prices = map(lambda x: x.text_content(), price)
        prices = [i for i in prices if i != ' ']

        return "/".join(prices)

    def parseDate(self, tag):
        datetmp = u""

        if tag != None and len(tag) == 0:
            return u""

        datetmp = "".join(tag.xpath('./a[@class="event-date-col"]/span/text()'))

        day, month, year = datetmp.split(".")
        return "%s-%.2d-%.2d" % (int(year), int(month), int(day))

    def parseEvent(self, tag):
        date = u""
        event = u""
        price = u""

        date = self.parseDate(tag)
        event = tag.xpath('./a[@class="event-details-col"]/h2/text()')
        event = " ".join(event).replace("\n", "")
        event = re.sub("\s+", " ", event)
        event = event.lstrip(" ").rstrip(" ")

        price = self.parsePrice(tag)

        return { u"venue" : self.getVenueName(), \
                 u"date" : date,                 \
                 u"name" : event,                \
                 u"price" : price }

    def parseEvents(self, data):
        doc = html.fromstring(data)

        for tag in doc.xpath('//div[starts-with(@class, "event-content")]' + \
                             '/*/div[@class="event-row"]'):
            yield self.parseEvent(tag)

if __name__ == '__main__':
    import requests

    d = Tavastia()
    r = requests.get(d.url)

    for i in d.parseEvents(r.content):
        for k, v in i.iteritems():
            print "%-10s: %s" % (k, v)
        print

