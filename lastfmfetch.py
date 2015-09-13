#!/usr/bin/env python
# -*- coding: utf-8 -*-

import lxml.html
import pylast
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

    def __dbInit(self, db):
        if db == None:
            self.db = db

    def __readAPIkeyUserInfo(self, fname):
        """
        First line must include username.
        Second line must include password.
        Third line must include API key.
        Fourth line must include API secret.
        """
        data = list()

        with open(fname, "r") as f:
            for line in f:
                data.append(line.replace("\n", ""))

        if len(data) < 4:
            raise LfmAPIkeyError("Error while reading API key and secret.")
        return (data[0], pylast.md5(data[1]), data[2], data[3])

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

    def nonAPIparser(self, username):
        """
        New LastFM is broken in many ways. This method omits their API and
        parses data directly from the website.
        """
        pageidx = 1
        libraryurl = "http://www.last.fm/user/%s/library/artists?page=%s" % \
                     (username, pageidx)
        p = re.compile("[0-9,]+")
        html = requests.get(libraryurl)
        site = lxml.html.fromstring(html.text).getroottree().getroot()

        for libitem in site.xpath('//tbody/tr'):
            artist = libitem.xpath('./td[@class="chartlist-name"]/span/a/text()')
            artist = " ".join(artist)

            playcount = libitem.xpath('./td[@class="chartlist-countbar"]/span/span/a/text()')
            playcount = " ".join(playcount)
            pcount = re.search(p, playcount)
            if pcount == None:
                raise PlaycountParseError
            pcount = pcount.group().replace(",", "")

            print {u"name" : artist, \
                   u"playcount" : pcount}

if __name__ == '__main__':
    allbands = list()
    lfmr = LastFmRetriever()

    #for i in lfmr.getAllListenedBands(2):
    #    print "%s"  % (i)
    lfmr.nonAPIparser("weezel_ding")

