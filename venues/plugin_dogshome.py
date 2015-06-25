# -*- coding: utf-8 -*-

from lxml.html import parse

import re


class Dogshome(object):
    def __init__(self):
        self.data = None

        self.url = "http://www.dogshome.fi/index.php?id=4"
        self.name = "Dog's home"

    def getVenueName(self):
        return self.name

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

    def getJSON(self):
        return ""


if __name__ == '__main__':
    import requests

    p = Dogshome()
    p.parseEvents("")

