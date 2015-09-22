#!/usr/bin/env python
# -*- coding: utf-8 -*-

import lxml.html
try:
    import pylast
    havePyLast = True
except ImportError:
    havePyLast = False
import re
import requests

FNAME = "APIKEYS"


class LfmUserError(Exception): pass
class LfmAPIkeyError(Exception): pass
class PlaycountParseError(Exception): pass

class LastFmRetriever(object):
    def __init__(self, db=None):
        self.__db = self.__dbInit(db)
        self.__username = None
        self.__password = None
        self.__apikey = None
        self.__apisecret = None

        self.__username,         \
             self.__password,    \
             self.__apikey,      \
             self.__apisecret = self.__readAPIkeyUserInfo(FNAME)

    def __dbInit(self, db): # TODO Currently this isn't being utilized
        if db == None:
            self.db = db

    def __readAPIkeyUserInfo(self, fname):
        """
        First line must include username.

        The following three lines are optional:
        Second line can include password.
        Third line can include API key.
        Fourth line can include API secret.
        """
        data = list()

        with open(fname, "r") as f:
            for line in f:
                data.append(line.replace("\n", ""))

        if len(data) == 1:
            return (data[0], None, None, None)
        elif len(data) == 4:
            return (data[0], pylast.md5(data[1]), data[2], data[3])
        else:
            raise LfmAPIkeyError("Error while reading API key and secret.")

    def getAllListenedBands(self, limit=None):
        """
        Retrieves the all listened bands by self.__username.

        Implemented in aggregate method nature so that it can be feed to SQL
        directly.

        Changing limit to 'None' will fetch all the listened artists in
        library.
        """
        # XXX This can be probably fed as a dict.
        network = pylast.get_lastfm_network(api_key = self.__apikey,       \
                                            api_secret = self.__apisecret, \
                                            username = self.__username,    \
                                            password_hash = self.__password)

        library = pylast.Library(self.__username, network)

        for artist in library.get_artists(limit):
            yield {u"name" : artist.item.name, \
                   u"playcount" : artist.playcount}

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
        site = lxml.html.fromstring(html.text).getroottree().getroot()

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

                playcount = libitem.xpath('./td[@class="chartlist-countbar"]/span/span/a/text()')
                playcount = " ".join(playcount)
                pcount = re.search(p, playcount)
                if pcount == None:
                    raise PlaycountParseError
                pcount = pcount.group().replace(",", "")

                yield {u"name" : artist, \
                       u"playcount" : pcount}

            # Fetch the next page
            pageidx += 1
            libraryurl = "http://www.last.fm/user/%s/library/artists?page=%s" % \
                         (self.__username, pageidx)
            html = requests.get(libraryurl)
            site = lxml.html.fromstring(html.text).getroottree().getroot()

if __name__ == '__main__':
    allbands = list()
    lfmr = LastFmRetriever()

    #for i in lfmr.getAllListenedBands(2):
    #    print "%s"  % (i)
    for i in lfmr.nonAPIparser():
        print "%s" % (i)

