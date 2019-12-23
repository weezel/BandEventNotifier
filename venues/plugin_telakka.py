#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import lxml.html

import re
import time
import datetime


class PluginParseError(Exception): pass

class Telakka(object):
    def __init__(self):
        self.url = "http://www.telakka.eu/ravintola/ohjelma"
        self.name = "Telakka"
        self.city = "Tampere"
        self.country = "Finland"

        # Parsing patterns
        self.pat_date = re.compile("[0-9]+.[0-9]+.")
        self.monetary = re.compile("[0-9,]+[ ]?€")

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

    def parsePrice(self, elem):
        if elem == '':
            return '0 €'

        prices = re.search(self.monetary, elem)
        if prices is None:
            return "0 €"
        return "".join(prices.group())

    def parseDate(self, elem):
        parsed_date = ""
        date_now = datetime.datetime.now()

        try:
            parsed = " ".join(elem.xpath('./strong/text()'))
            # TODO Use walrus operator
            # FIXME year swap
            if re.search(self.pat_date, parsed):
                parsed_date = re.search(self.pat_date, parsed).group()
                parsed_date2 = f'{parsed_date}{date_now.year}'
                return datetime.datetime.strptime(parsed_date2, "%d.%m.%Y")
        except Exception:
            return ""

    def parseEvents(self, data):
        doc = lxml.html.fromstring(data)

        for et in doc.xpath('//div[@class="entry-content"]/p/span[@style="color: #ff6600;"]'):
            event_date = self.parseDate(et)
            if event_date is None:
                continue

            tmp = "".join(et.xpath("../text()")).replace("\r\n", " ")
            event = re.sub("\s+", " ", tmp).strip()
            price = self.parsePrice(event)

            tmp = "".join(et.xpath('../strong/text()')).replace("\r\n", " ")
            has_title = re.sub("\s+", " ", tmp).strip()

            if has_title != "":
                ename = "{}: {}".format(has_title, event)
            else:
                ename = event

            yield { "venue" : self.getVenueName(),
                    "date" : event_date,
                    "name" : ename,
                    "price" : price }


if __name__ == '__main__':
    import requests

    p = Telakka()
    r = requests.get(p.url)

    for e in p.parseEvents(r.content):
        for k, v in e.items():
            print(f"{k:>10s}: {v}")
        print

