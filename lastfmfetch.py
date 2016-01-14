#!/usr/bin/env python
# -*- coding: utf-8 -*-

import lxml.html
import requests

import re

FNAME = "USERNAME"


class LfmUserError(Exception): pass

class LastFmRetriever(object):
    def __init__(self, db=None):
        self.__db = self.__dbInit(db)
        self.__username = None

        self.__username = self.__readUsername(FNAME)

    def __dbInit(self, db): # TODO Currently this isn't being utilized
        if db == None:
            self.db = db

    def __readUsername(self, fname):
        """
        First line of the file must include a username.
        """
        data = list()

        with open(fname, "r") as f:
            for line in f:
                data.append(line.replace("\n", ""))

        if len(data) == 1:
            return data[0]

    def calculatePopularity(self, allbands, thisband):
        totalplaycount = sum([artist.playcount for artist in allbands])
        return float(thisband.playcount) / totalplaycount * 1000

    def nonAPIparser(self):
        """
        New LastFM is broken in many ways. This method omits their API and
        parses data directly from the website.
        """
        pageidx = 1
        p = re.compile("[0-9,]+")
        libraryurl = "http://www.last.fm/user/%s/library/artists?page=1" % \
                     (self.__username)
        html = requests.get(libraryurl)
        site = lxml.html.fromstring(html.content)

        pagestag = site.xpath('//ul[@class="pagination"]' \
                              +'/li[@class="pages"]/text()')
        pagescount = re.findall("[0-9,]+", " ".join(pagestag)) # [1, n]
        if len(pagescount) == 0:
            pagescount = 1 # Otherwise loop would be skipped
        else:
            pagescount = int(pagescount[1])

        # Go through the all pages
        while pageidx <= pagescount:
            for libitem in site.xpath('//tbody/tr'):
                artist = libitem.xpath('./td[@class="chartlist-name"]/span/a/text()')
                artist = " ".join(artist)

                # Bail early, no need to parse further.
                # Since we use fairly eager matching, LastFM's newest changes
                # hit in this rule too.
                # The mismatch is cause by "Listening History" charts.
                if artist == "":
                    continue

                playcount = libitem.xpath('./td[@class="chartlist-countbar"]' \
                                        + '/span/span/a/text()')
                playcount = " ".join(playcount)
                pcount = re.search(p, playcount)
                pcount = pcount.group().replace(",", "")

                yield {u"name" : artist, \
                       u"playcount" : pcount}

            # Fetch the next page
            pageidx += 1
            libraryurl = "http://www.last.fm/user/%s/library/artists?page=%s" \
                    % (self.__username, pageidx)
            html = requests.get(libraryurl)
            site = lxml.html.fromstring(html.text).getroottree().getroot()

if __name__ == '__main__':
    allbands = list()
    lfmr = LastFmRetriever()

    for i in lfmr.nonAPIparser():
        print "%s" % (i)

