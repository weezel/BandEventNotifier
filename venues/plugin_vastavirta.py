# -*- coding: utf-8 -*-

import lxml.html
import re


class Vastavirta(object):
    def __init__(self):
        self.data = None

        self.url = "http://vastavirta.net/fi/"
        self.name = "Vastavirta"
        self.city = "Tampere"
        self.country = "Finland"
        self.parseddata = None
        self.monthmap = {   \
                "Tam" : 1,  \
                "Hel" : 2,  \
                "Maa" : 3,  \
                "Huh" : 4,  \
                "Tou" : 5,  \
                "Kes" : 6,  \
                "Hei" : 7,  \
                "Elo" : 8,  \
                "Syy" : 9,  \
                "Lok" : 10, \
                "Mar" : 11, \
                "Jou" : 12 }

    def getVenueName(self):
        return self.name

    def getCity(self):
        return self.city

    def getCountry(self):
        return self.country

    def eventSQLentity(self):
        return { u"name" : self.name, \
                 u"city" : self.city, \
                 u"country" : self.country }

    def parsePrice(self, tag):
        parsedprice = tag.xpath('.//div[@class="event-details"]/*/text()')
        prices = " ".join(parsedprice)

        if prices:
            return u"%s" % (prices)
        else:
            return u"0"

    def parseDate(self, tag):
        day = tag.xpath('./*/div[@class="start-date"]/div[@class="event-day"]/text()')
        m = tag.xpath('./*/div[@class="start-date"]/div[@class="event-month"]/text()')
        year = tag.xpath('./*/div[@class="start-date"]/div[@class="event-year"]/text()')

        day = " ".join(day)
        month = " ".join(m)
        year = " ".join(year)

        if day is "" or month is "" or year is "":
            return ""

        month = self.monthmap[month]
        return "%.4d-%.2d-%.2d" % (int(year), int(month), int(day))

    def parseEvent(self, event):
        date = self.parseDate(event)
        etitle = " ".join(event.xpath('./*/div[@class="event-title"]/*/text()'))
        prices = self.parsePrice(event)

        return { u"venue" : self.getVenueName(), \
                 u"date" : date,                 \
                 u"name" : etitle,               \
                 u"price" : prices }

    def parseEvents(self, data):
        doc = lxml.html.fromstring(data).getroottree().getroot()
        tags = doc.xpath('//div[@class="event-list"]/ul' \
                       + '[@class="event-list-view"]'    \
                       + '/li[@class="event "]')
        tmp = u""

        for event in reversed(tags):
            parsed = self.parseEvent(event)

            if parsed["date"] == "":
                tmp += ", " + parsed["name"]
            else:
                parsed ["name"] += tmp
                yield parsed
                tmp = u""

if __name__ == '__main__':
    import requests

    v = Vastavirta()
    r = requests.get(v.url)

    #with open("venues/vastavirta.html") as f:
    #    r = f.read()

    for event in v.parseEvents(r.text):
        for k, v in event.iteritems():
            print "%-10s: %s" % (k, v)
        print

