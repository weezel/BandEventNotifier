# -*- coding: utf-8 -*-

from lxml.html import parse

import time
import re


class Dogshome(object):
    def __init__(self):
        self.url = "http://www.dogshome.fi/index.php?id=4"
        self.name = "Dog's home"
        self.city = "Tampere"
        self.country = "Finland"

        # Parsing patterns
        self.datestartpat = re.compile("^\d+\.\d+. ")
        self.monetarypattern = re.compile("[0-9.,]+ e")

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
        return {u"name" : self.name, \
                u"city" : self.city, \
                u"country" : self.country}

    def parsePrice(self, line):
        linetmp = line.replace(u"€", u" e")
        prices = re.findall(self.monetarypattern, linetmp)

        return map(lambda p: p.replace(" ", "").strip(","), prices)

    def parseDate(self, line):
        # TODO Doesn't handle year changes yet.
        date = re.search(self.datestartpat, line)
        if date is not None:
            year = time.strftime("%Y")
            day, month = date.group().strip(" ").rstrip(".").split(".")
            date = "%s-%s-%s" % (year, month, day)
        else:
            date = ""
        return unicode(date)

    def parseEvent(self, line):
        dateends = line.find(" ") + 1

        if dateends > 0:
            return unicode(line[dateends :])
        return unicode("")

    def parseEvents(self, data):
        doc = parse("doggari.html").getroot()
        eventtags = doc.cssselect('div.innertube p')
        container = list()

        # XXX First line advertises a pub quiz, not useful for us.
        # XXX Last three lines aren't needed either, those are:
        #       - Free entry until otherwise mentioned
        #       - All rights reserved
        #       - Past events
        for line in eventtags[1 : len(eventtags) - 3]:
            lineastext = line.text_content()

            # We could omit the aforementioned adverts by re-defining iteration
            # ranges but I don't trust that the empty lines count will remain
            # constant.
            # More robust this way.
            if lineastext is None or len(lineastext) == 1:
                continue

            # Real event...
            if re.search(self.datestartpat, lineastext) != None:
                container.append(lineastext.strip("\n"))
            # ...more info on the next line, description or start time, join to
            # the previously parsed line.
            else:
                container[len(container) - 1] += " " + lineastext.strip("\n")

           # FIXME for some reason this skips the joined lines.
           # eventinfo = container[len(container) - 1]
           # yield { u"venue" : self.getVenueName(),   \
           #     u"date" : self.parseDate(eventinfo),      \
           #     u"event" : self.parseEvent(eventinfo),    \
           #     u"price" : self.parsePrice(eventinfo) }

        for event in container:
            yield { u"venue" : self.getVenueName(),    \
                    u"city" : self.getCity(),          \
                    u"country" : self.getCountry(),    \
                    u"date" : self.parseDate(event),   \
                    u"event" : self.parseEvent(event), \
                    u"price" : self.parsePrice(event) }

if __name__ == '__main__':
    p = Dogshome()

    #print p.parseEvents("")
    import json
    daa = p.parseEvents("")
    for i in daa:
        print "Keys = %s" % i.keys()
        print "Data = %s" % i
        print

