# -*- coding: utf-8 -*-

from lxml import html

import time
import re

class PluginParseError(Exception): pass

class Yotalo(object):
    def __init__(self):
        self.url = "http://www.yo-talo.fi"
        self.name = "Yo-talo"
        self.city = "Tampere"
        self.country = "Finland"
        self.parseddata = None

        # Parsing patterns
        self.datestartpat = re.compile(" \d+\.\d+.$")
        self.monetarypattern = re.compile("[0-9.,]+([ ])?e(uroa)?")

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

    def parsePrice(self, line):
        # FIXME Regexp is broken, fit it at some point
        # Spotted at these possible monetary variations:
        #   12 euroa
        #   12e
        #   12 EUROA
        #   12 Euroa
        prices = re.findall("[0-9.,]+([ ]) e(uroa)?", line, flags=re.IGNORECASE)
        return "{} €".format("/".join(prices))

    def parseDate(self, line):
        year = int(time.strftime("%Y"))
        month_now = time.strftime("%m")

        if line is None:
            return ""

        date = re.search(self.datestartpat, " ".join(line))
        if date is None:
            return ""

        date = date.group().lstrip(" ").rstrip(".")
        day, month = date.split(".")

        # Year has changed since the parsed month is smaller than the current
        # month.
        if int(month) < int(month_now):
            year += 1

        return "{:4d}-{:2d}-{:2d}".format(year, int(month), int(day))

    def parseEvent(self, tag):
        date = ""
        title = ""
        desc = ""

        date = self.parseDate(tag.xpath('./div[@class="item_left"]/text()'))
        title = " ".join(tag.xpath('./div[@class="item_center"]/h3/a/text()'))
        for a in tag.xpath('./div[@class="item_center"]/p'):
            desc += " " + " ".join(a.xpath('./*/text()'))
        desc = re.sub("\s+", " ", desc)
        desc = desc.lstrip(" ").rstrip(" ")
        name = "%s - %s" % (title, desc)
        name = re.sub("\s+", " ", name)
        price = self.parsePrice(name)

        return { "venue" : self.getVenueName(), \
                 "date" : date, \
                 "name" : name, \
                 "price" : price }

    def parseEvents(self, data):
        #doc = parse("venues/doggari.html").getroot()
        doc = html.fromstring(data)

        for item in doc.xpath('//div[@id="left"]/div[@class="item"]'):
            yield self.parseEvent(item)

if __name__ == '__main__':
    import requests

    y = Yotalo()
    r = requests.get(d.url)

    for e in y.parseEvents(r.content):
        for k, v in e.items():
            print(f"{k:>10s}: {v}")
        print

