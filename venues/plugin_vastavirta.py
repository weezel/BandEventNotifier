# -*- coding: utf-8 -*-

from lxml import html
from absvenueparser import AbsVenueParser

import requests
import re


class Vastavirta(AbsVenueParser):
    def __init__(self):
        super(AbsVenueParser, self).__init__()
        self.data = None

        self.url = "http://vastavirta.net/tulevat.html"
        self.venuename = "Vastavirta"

    def getVenue(self):
        return self.venuename

    def parseArtists(self, data):
        pass

    def clean_output(self, text):
        tmp = re.sub("\s+", " ", text)
        tmp = re.sub("\t+", " ", tmp)
        return re.sub("[\r\n]+", "", tmp).lstrip(" ")

    def parseEvents(self, data):
        doc = html.parse("vastavirta.html").getroot()
        for e in doc.cssselect('table > tr > td')[3]:
            for elem in e.cssselect("font"):
                parsed = elem.text

                if elem.items()[0][1] != "#000000":
                    continue
                if type(parsed) is type(str()) or type(parsed) is type(unicode()):
                #if parsed == None or type(parsed) == list() or \
                #        parsed.startswith(u"Kaikkien keikkojen") or \
                #        parsed.startswith(u"Muutokset mahdollisia"):
                #    continue
                #print type(elem.items()[0][1]) #["color"]
                    #print elem.items()[0][1]

                    #print type(elem)
                    cleaned = self.clean_output(parsed)
                    print "%s" % cleaned


if __name__ == '__main__':
    p = Vastavirta()
    p.parseEvents("")

