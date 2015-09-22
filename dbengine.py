#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sqlite3

dbname = "bandevents.db"


class DBEngine(object):
    def __init__(self):
        self.conn = None
        self.cur = None
        self.__firstRun()

    def __firstRun(self):
        if self.conn == None:
            self.conn = sqlite3.connect(dbname)
        if self.cur == None:
            self.cur = self.conn.cursor()

    def close(self):
        if self.cur:
            self.cur.close()
        if self.conn:
            self.conn.close()

    def pluginCreateVenueEntity(self, venuedict):
        """
        Create needed venue entries.

        Parameter venuedict is Dogshome.eventSQLentity(), i.e.
        """
        cols = ", ".join(venuedict.keys())
        placeholders = ":" + ", :".join(venuedict.keys())
        q = u"INSERT OR IGNORE INTO venue (%s) VALUES (%s);" \
                % (cols, placeholders)
        self.cur.execute(q, venuedict)
        self.conn.commit()

    def insertVenueEvents(self, venue):
        """
        Insert parsed events from a venue into the database.
        """
        # Replace venue by venueid
        venue["venueid"] = self.getVenueByName(venue["venue"])[0]
        # TODO Why do we have this keyword in the dict in general...
        venue.pop("venue") # No such column in SQL db
        cols = ", ".join(venue.keys())
        placeholders = ":" + ", :".join(venue.keys())
        q = u"INSERT OR IGNORE INTO event (%s) VALUES (%s);" \
                % (cols, placeholders)
        self.cur.execute(q, venue)
        self.conn.commit()

    def insertLastFMartists(self, artistdata):
        cols = ", ".join(artistdata.keys())
        placeholders = ":" + ", :".join(artistdata.keys())
        q = u"INSERT OR IGNORE INTO artist (%s) VALUES (%s);" \
                % (cols, placeholders)
        self.cur.execute(q, artistdata)
        self.conn.commit()

    def getVenues(self):
        q = u"SELECT id, name, city, country FROM venue"
        results = self.cur.execute(q)
        return results.fetchall()

    def getVenueByName(self, vname):
        q = u"SELECT id, name, city, country FROM venue " \
           + "WHERE name = ? LIMIT 1;"
        results = self.cur.execute(q, [vname])
        return results.fetchone()

    def getAllGigs(self):
        q = u"SELECT DISTINCT e.date, v.name, e.name "                    \
           + "FROM event AS e INNER JOIN venue AS v ON e.venueid = v.id " \
           + "GROUP BY e.date, v.name ORDER BY e.date;"
        results = self.cur.execute(q)
        return results.fetchall()

    def getArtists(self):
        q = u"SELECT name, playcount FROM artist;"
        results = self.cur.execute(q)
        for artist, playcount in results.fetchall():
            yield {u"artist" : artist, \
                   u"playcount" : playcount}

    def getArtist(self, aname):
        pass # TODO

    def purgeOldEvents(self):
        pass # TODO

if __name__ == '__main__':
    import venues.plugin_dogshome

    db = DBEngine()
    doggari = venues.plugin_dogshome.Dogshome()

    db.pluginCreateVenueEntity(doggari.eventSQLentity())
    assert(db.getVenues() == [(1, u"Dog's home", u'Tampere', u'Finland')])
    assert(db.getVenueByName("Dog's home") == (1, u"Dog's home", u'Tampere', u'Finland'))
    assert(db.getVenueByName("Testijuottola that should fail") == None)
    #db.insertVenueEvents(doggari.parseEvents(""))

    ### Test LastFM retriever
    import lastfmfetch

    lfmr = lastfmfetch.LastFmRetriever(db)
    for artist in lfmr.getAllListenedBands(limit=5):
        db.insertLastFMartists(artist)

    db.close()

