#!/usr/bin/env python3

import datetime
import lxml.html

import re


class PluginParseError(Exception): pass

class Glivelabtampere(object):
    def __init__(self):
        self.url = "https://www.glivelab.fi/tampere/"
        self.name = "G Livelab"
        self.city = "Tampere"
        self.country = "Finland"

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

    def parseDate(self, tag):
        year = datetime.datetime.now().year
        day, month, _ = tag.split(".")
        return "%.4d-%.2d-%.2d" % (int(year), int(month), int(day))

    def normalize_string(self, s):
        rm_spaces = re.sub("\+s", " ", s)
        rm_left_padding = re.sub("^\s+", "", rm_spaces)
        rm_right_padding = re.sub("\s+$", "", rm_left_padding)
        return rm_right_padding

    def parseEvent(self, tag):
        date = ""
        title = ""
        artist = ""
        desc = ""
        price = 0

        for node in tag:
            # XXX I have no idea why the xpath mentioned in parseEvents()
            # doesn't work as intended. I cannot see two 'div' child nodes with
            # 'a' as a parent as I would expect.
            #
            # Hence, go back one node and list all of it's descendants.
            prev_nodes = node.xpath('../*')
            if len(prev_nodes) != 2:
                raise PluginParseError("Failed to parse GliveLab Tampere")
            # First node is "img-wrapper" which we are not interested
            title = " ".join(prev_nodes[1].xpath('./div/h2/text()'))
            title = self.normalize_string(title)
            date = " ".join(prev_nodes[1].xpath('./div/div[@class="date"]/text()'))
            date = self.parseDate(self.normalize_string(date))
            time = " ".join(prev_nodes[1].xpath('./div/div[@class="time"]/text()'))
            time = self.normalize_string(time)

            price = "0€"

            return { "venue" : self.getVenueName(),  \
                     "date" : date,                   \
                     "name" : "%s" % (title), \
                     "price" : price }

    def parseEvents(self, data):
        doc = lxml.html.fromstring(data)
        eventtags = doc.xpath('//li[@class="item"]/a')

        for et in eventtags:
            yield self.parseEvent(et)

if __name__ == '__main__':
    import requests

    g = GLivelabTampere()
    r = requests.get(g.url)

    for e in g.parseEvents(r.content):
        for k, v in e.items():
            print(f"{k:>10s}: {v}")
        print

