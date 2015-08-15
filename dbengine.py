#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sqlite3

dbname = "bandevents.db"


class DBEngine(object):
    def __init__(self):
        self.conn = None
        self.cur = None
        self.__firstRun()
        self.venues = dict()

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

        # Query events now, will be {venue name : venueid}
        self.venues.update({venuedict["name"] : self.cur.lastrowid})

    def insertVenueEvents(self, venueaggr):
        """
        Insert parsed events from a venue to database.
        """
        for event in venueaggr:
            # Replace venue by venueid
            event["venueid"] = self.venues[event["venue"]] # This is venueid
            event.pop("venue")
            cols = ", ".join(event.keys())
            placeholders = ":" + ", :".join(event.keys())
            q = u"INSERT OR IGNORE INTO event (%s) VALUES (%s);" \
                    % (cols, placeholders)
            self.cur.execute(q, event)
        self.conn.commit() #XXX All processed, commit

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

    def intersectLastFmAndEvents(self):
        # TODO
        pass

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

