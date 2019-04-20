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
                "Tammi" : 1,  \
                "Helmi" : 2,  \
                "Maalis" : 3,  \
                "Huhti" : 4,  \
                "Touko" : 5,  \
                "Kesä" : 6,  \
                "Heinä" : 7,  \
                "Elo" : 8,  \
                "Syys" : 9,  \
                "Loka" : 10, \
                "Marras" : 11, \
                "Joul" : 12 }

    def getVenueName(self):
        return self.name

    def getCity(self):
        return self.city

    def getCountry(self):
        return self.country

    def eventSQLentity(self):
        return { "name" : self.name, \
                 "city" : self.city, \
                 "country" : self.country }

    def parsePrice(self, tag):
        parsedprice = tag.xpath('.//div[@class="event-details"]/*/text()')
        prices = " ".join(parsedprice)

        if prices:
            return "%s" % (prices)
        else:
            return "0"

    def parseDate(self, tag):
        day = tag.xpath('./*/div[@class="start-date"]/div[@class="event-day"]/text()')
        m = tag.xpath('./*/div[@class="start-date"]/div[@class="event-month"]/text()')
        year = tag.xpath('./*/div[@class="start-date"]/div[@class="event-year"]/text()')

        day = " ".join(day)
        month = " ".join(m).capitalize()
        year = " ".join(year)

        if day is "" or month is "" or year is "":
            return ""

        month = self.monthmap[month]
        return "%.4d-%.2d-%.2d" % (int(year), int(month), int(day))

    def parseEvent(self, event):
        date = self.parseDate(event)
        etitle = " ".join(event.xpath('./*/div[@class="event-title"]/*/text()'))
        prices = self.parsePrice(event)

        return { "venue" : self.getVenueName(), \
                 "date" : date,                 \
                 "name" : etitle,               \
                 "price" : prices }

    def parseEvents(self, data):
        doc = lxml.html.fromstring(data).getroottree().getroot()
        tags = doc.xpath('//div[@class="event-list"]/ul' \
                       + '[@class="event-list-view"]'    \
                       + '/li[@class="event "]')
        tmp = ""

        for event in reversed(tags):
            parsed = self.parseEvent(event)

            if parsed["date"] == "":
                tmp += ", " + parsed["name"]
            else:
                parsed ["name"] += tmp
                yield parsed
                tmp = ""

if __name__ == '__main__':
    import requests

    v = Vastavirta()
    r = requests.get(v.url)

    #with open("venues/vastavirta.html") as f:
    #    r = f.read()

    for event in v.parseEvents(r.content):
        for k, v in event.items():
            print(f"{k:>10s}: {v}")
        print

