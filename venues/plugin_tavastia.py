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
        return { "name" : self.name, \
                 "city" : self.city, \
                 "country" : self.country }

    def parsePrice(self, tag):
        prices = tag.xpath('./a[@class="event-details-col"]/' + \
                          'p[@class="event-details"]' +        \
                          '/span[@class="event-priceinfo"]')
        prices = [i.text_content() for i in prices \
                    if i.text_content() != ' ']

        return "/".join(prices)

    def parseDate(self, tag):
        datetmp = ""

        if tag != None and len(tag) == 0:
            return ""

        datetmp = "".join(tag.xpath('./a[@class="event-date-col"]/span/text()'))

        day, month, year = datetmp.split(".")
        return "%s-%.2d-%.2d" % (int(year), int(month), int(day))

    def parseEvent(self, tag):
        date = ""
        event = ""
        price = ""

        date = self.parseDate(tag)
        event = tag.xpath('./a[@class="event-details-col"]/h2/text()')
        event = " ".join(event).replace("\n", "")
        event = re.sub("\s+", " ", event)
        event = event.lstrip(" ").rstrip(" ")

        price = self.parsePrice(tag)

        return { "venue" : self.getVenueName(), \
                 "date" : date,                 \
                 "name" : event,                \
                 "price" : price }

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
        for k, v in i.items():
            print(f"{k:>10s}: {v}")
        print

