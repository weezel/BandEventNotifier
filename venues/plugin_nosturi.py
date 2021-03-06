#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import lxml.html

import re


class PluginParseError(Exception): pass

class Nosturi(object):
    def __init__(self):
        self.url = "http://elmu.fi/keikat"
        self.name = "Nosturi"
        self.city = "Helsinki"
        self.country = "Finland"

        # Parsing patterns
        self.datepat = re.compile("[0-9.]+")

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
        if not line:
            return "0"
        line = line[0]
        price = line.replace("\n", "")
        price = re.sub("\s+", "", price)
        return price.replace(",", ".")

    def parseDate(self, tag):
        if tag is None:
            return ""

        d = tag[0].text_content()
        datesplit = re.search(self.datepat, d)

        if datesplit:
            day, month, year = datesplit.group().split(".")
        else:
            return ""

        return "%.4d-%.2d-%.2d" % (int(year), int(month), int(day))

    def parseEvent(self, tag):
        """
        <span> Title
        <h4>   Artist
        <p>    Description
        <div>  Time/doors
        """

        date = ""
        title = ""
        artists = ""
        summary = ""

        date = self.parseDate(tag.xpath('.//span[@class="date-display-single"]'))
        title = " ".join(tag.xpath('.//div[@class="keikka_otsikko "]/a/text()'))
        artists = " ".join(tag.xpath('.//div[@class="artistit"]/a/text()'))
        summary = tag.xpath('.//div[@class="summary"]')[0].text_content()
        price = self.parsePrice(tag.xpath('.//span[@class="hinta "]/text()'))

        name = "%s %s %s" % (title, artists, summary)
        name = name.replace('\n', '')
        name = re.sub("\s+", " ", name).lstrip(" ").rstrip(" ")

        return { "venue" : self.getVenueName(), \
                 "date" : date,                 \
                 "name" : name,                 \
                 "price" : price }

    def parseEvents(self, data):
        doc = lxml.html.fromstring(data)

        for event in doc.xpath('//div[@class="keikkainfo"]'):
            yield self.parseEvent(event)

if __name__ == '__main__':
    import requests

    k = Nosturi()
    r = requests.get(k.url)

    for e in k.parseEvents(r.content):
        for k, v in e.items():
            print(f"{k:>10s}: {v}")
        print

