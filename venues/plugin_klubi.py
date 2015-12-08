#!/usr/bin/env python
# -*- coding: utf-8 -*-

import lxml.html

import re


class PluginParseError(Exception): pass

class Klubi(object):
    def __init__(self):
        self.url = "http://www.tullikamari.net/fi/klubi/ohjelma"
        self.name = "Klubi"
        self.city = "Tampere"
        self.country = "Finland"

        # Parsing patterns
        self.datepat = re.compile("[0-9]{,2}.[0-9]{,2}.[0-9]{4}")

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
        return u"0" if "-" in line else u"%s€" % line

    def parseDate(self, tag):
        date = re.search(self.datepat, tag)
        if date == None:
            return u""

        day, month, year = date.group().split(".")
        return "%.4d-%.2d-%.2d" % (int(year), int(month), int(day))

    def parseEvent(self, tag):
        """
        <span> Title
        <h4>   Artist
        <p>    Description
        <div>  Time/doors
        """

        date = u""
        title = u""
        artist = u""
        desc = u""

        datedata = " ".join(tag.xpath('./span[@class="date "]/text()'))
        date = self.parseDate(datedata)

        for node in tag.xpath('./div[@class="event-content"]'):
            title = " ".join(node.xpath('./span[@class="title"]/a/text()'))
            title = re.sub("\s+", " ", title).rstrip("\n").rstrip(" ")

            artist = ", ".join([a for a in node.xpath('./h4[@class="artist"]/h4/a/text()')])
            artist = re.sub("\s+", " ", artist).rstrip("\n").lstrip(" ").rstrip(" ")

            desc = " ".join(node.xpath('./p/text()'))
            desc = re.sub("\s+", " ", desc).lstrip(" ").rstrip("\n").rstrip(" ")

            price = self.parsePrice( \
                    " ".join(node.xpath('./div[@class="info"]' \
                               + '/span[@class="price"]/text()')))

            return { u"venue" : self.getVenueName(),  \
                     u"date" : date,                   \
                     u"name" : "%s%s %s" % (title, artist, desc), \
                     u"price" : price }

    def parseEvents(self, data):
        doc = lxml.html.fromstring(data)
        eventtags = doc.xpath('//ul[@class="upcoming-events-list"]/li')

        for et in eventtags:
            yield self.parseEvent(et)

if __name__ == '__main__':
    import requests

    k = Klubi()
    r = requests.get(k.url)

    for e in k.parseEvents(r.content):
        for k, v in e.iteritems():
            print "%-10s: %s" % (k, v)
        print

