#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pylast

FNAME = "APIKEYS"


class LfmUserError(Exception): pass
class LfmAPIkeyError(Exception): pass

class LastFmRetriever(object):
    def __init__(self, db=None):
        self.__db = self.__dbInit(db)
        self.__apikey = None
        self.__apisecret = None

        self.__apikey, self.__apisecret = self.__readAPIkey(FNAME)

    def __dbInit(self, db):
        if db == None:
            self.db = db

    def __readAPIkey(self, fname):
        """
        First line must include API key.
        Second line must include API secret.
        """
        data = list()

        with open(fname, "r") as f:
            for line in f:
                data.append(line.replace("\n", ""))

        if len(data) < 2:
            raise LfmAPIkeyError("Error while reading API key and secret.")
        return (data[0], data[1])

    def getAllListenedBands(self, username, limit=None):
        """
        Retrieves the all listened bands of a username.

        Implemented in aggregate method nature so that it can be feed to SQL
        directly.

        Changing limit to 'None' will fetch all the listened artists in
        library.
        """
        network = pylast.get_lastfm_network(self.__apikey, self.__apisecret)
        if username == None or len(username) < 1:
            raise LfmUserError("Error while fetching " \
                  + "username '%s' related data" % username)

        library = pylast.Library(username, network)

        for artist in library.get_artists(limit):
            yield {u"name" : artist.item.name, \
                   u"playcount" : artist.item.get_playcount()}

    def calculatePopularity(self, allbands, thisband):
        totalplaycount = sum([artist.playcount for artist in allbands])
        return float(thisband.playcount) / totalplaycount * 1000

if __name__ == '__main__':
    allbands = list()
    lfmr = LastFmRetriever()

    for i in lfmr.getAllListenedBands("weezel_ding"):
        print i,

