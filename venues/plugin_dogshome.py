# -*- coding: utf-8 -*-

from lxml import html

import time
import re

class PluginParseError(Exception): pass

class Dogshome(object):
    def __init__(self):
        self.url = "http://www.dogshome.fi/index.php?id=4"
        self.name = "Dog's home"
        self.city = "Tampere"
        self.country = "Finland"
        self.parseddata = None

        # Parsing patterns
        self.datestartpat = re.compile("^\d+\.\d+. ")
        self.monetarypattern = re.compile(u"[0-9.,]+€")

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

        return "/".join(prices)

    def parseDate(self, line):
        month_now = time.strftime("%m")
        year = int(time.strftime("%Y"))

        date = re.search(self.datestartpat, line)
        if date is not None:
            day, month = date.group().strip(" ").rstrip(".").split(".")
            # Are we on the new year already?
            if int(month) < int(month_now):
                year += 1
            date = "%s-%.2d-%.2d" % (int(year), int(month), int(day))
        else:
            date = ""
        return unicode(date)

    def parseEvent(self, line):
        dateends = line.find(" ") + 1

        if dateends > 0:
            return unicode(line[dateends :])
        return unicode("")

    def parseEvents(self, data):
        # XXX Double line event entries will likely fail
        doc = html.fromstring(data)
        eventpattern = re.compile("^[0-9]+\.[0-9].?")

        for line in doc.xpath('//div[@class="innertube"]/p'):
            #lineastext = line.text_content()
            if line.attrib.has_key("style") and \
               line.attrib['style'] == "text-align: center;":
                   if re.search(eventpattern, line.text_content()):
                       eventastext = line.text_content()
                       yield { u"venue" : self.getVenueName(),         \
                               u"date" : self.parseDate(eventastext),  \
                               u"name" : self.parseEvent(eventastext), \
                               u"price" : self.parsePrice(eventastext) }

if __name__ == '__main__':
    import requests

    d = Dogshome()
    r = requests.get(d.url)
    daa = d.parseEvents(r.content)

    for i in daa:
        for k, v in i.iteritems():
            print "%-10s: %s" % (k, v)
        print

