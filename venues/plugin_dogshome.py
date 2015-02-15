# -*- coding: utf-8 -*-

from lxml.html import parse
from absvenueparser import AbsVenueParser

import requests
import re


class Dogshome(AbsVenueParser):
    def __init__(self):
        super(AbsVenueParser, self).__init__()
        self.data = None

        self.url = "http://www.dogshome.fi/index.php?id=4"
        self.venue = "Dog's home"

    def getVenue(self):
        return self.venue

    def parseArtists(self, data):
        pass

    def parseEvents(self, data):
        doc = parse("doggari.html").getroot()
        for line in doc.cssselect('div.innertube p'):
            lineparsed = line.text
            if lineparsed is not None and len(lineparsed) > 1:
                try:
                    print lineparsed.tail
                except:
                    print lineparsed


if __name__ == '__main__':
    p = Dogshome()
    p.parseEvents("")

