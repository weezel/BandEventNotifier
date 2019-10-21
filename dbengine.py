#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
import threading

dbname = "bandevents.db"


def init_db():
    sql_schema = ""

    with open("schema.sql", "r") as f:
        sql_schema = f.readlines()

    with sqlite3.connect(dbname) as conn:
        cur = conn.cursor()
        for stmt in sql_schema:
            cur.execute(stmt)
        conn.commit()

class DBEngine(object):
    def __init__(self):
        self.conn = None
        self.cur = None
        self.__firstRun()
        self.lock = threading.Lock()

    def __firstRun(self):
        if self.conn == None:
            self.conn = sqlite3.connect(dbname)
        if self.cur == None:
            self.cur = self.conn.cursor()

    def close(self):
        with self.lock:
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
        q = "INSERT OR IGNORE INTO venue (%s) VALUES (%s);" \
                % (cols, placeholders)
        with self.lock:
            self.cur.execute(q, venuedict)
            self.conn.commit()

    def insertVenueEvents(self, venue):
        """
        Insert parsed events from a venue into the database.
        """
        with self.lock:
            # Replace venue by venueid
            venue["venueid"] = self.getVenueByName(venue["venue"])[0]
            # TODO Why do we have this keyword in the dict in general...
            venue.pop("venue") # No such column in SQL db
            cols = ", ".join(venue.keys())
            placeholders = ":" + ", :".join(venue.keys())
            q = "INSERT OR IGNORE INTO event (%s) VALUES (%s);" \
                    % (cols, placeholders)
            self.cur.execute(q, venue)
            self.conn.commit()

    def insertLastFMartists(self, artist, playcount):
        q = "INSERT OR REPLACE INTO artist (name, playcount) VALUES (?, ?);"
        with self.lock:
            self.cur.execute(q, [artist, playcount])
            self.conn.commit()

    def getVenues(self):
        q = "SELECT id, name, city, country FROM venue"
        results = self.cur.execute(q)
        return results.fetchall()

    def getVenueByName(self, vname):
        q = "SELECT id, name, city, country FROM venue " \
            + "WHERE name = ? LIMIT 1;"
        results = self.cur.execute(q, [vname])
        return results.fetchone()

    def getAllGigs(self):
        q = "SELECT DISTINCT e.date, v.name, v.city, e.name "            \
            + "FROM event AS e INNER JOIN venue AS v ON e.venueid = v.id " \
            + "GROUP BY e.date, v.name ORDER BY e.date ASC;"
        results = self.cur.execute(q)
        return results.fetchall()

    def getArtists(self):
        q = "SELECT name, playcount FROM artist;"
        results = self.cur.execute(q)
        for artist, playcount in results.fetchall():
            yield {"artist" : artist, \
                   "playcount" : playcount}

    def getArtist(self, aname):
        q = "SELECT name, playcount FROM artist " \
            + "WHERE name = ? LIMIT 5;"
        results = self.cur.execute(q, [aname])
        for artist, playcount in results.fetchall():
            yield { "artist" : artist, \
                    "playcount" : playcount }

    def purgeOldEvents(self):
        q = "DELETE FROM event " \
            + "WHERE strftime('%Y-%m-%d', date) < date('now');"
        with self.lock:
            self.cur.execute(q)
            self.conn.commit()

if __name__ == '__main__':
    db = DBEngine()

    def testDogsHomePlugin():
        import venues.plugin_dogshome

        doggari = venues.plugin_dogshome.Dogshome()

        db.pluginCreateVenueEntity(doggari.eventSQLentity())
        assert(db.getVenues() == [(1, "Dog's home", 'Tampere', 'Finland')])
        assert(db.getVenueByName("Dog's home") == (1, "Dog's home", \
               'Tampere', 'Finland'))
        assert(db.getVenueByName("Testijuottola that should fail") == None)
        db.insertVenueEvents(doggari.parseEvents(""))

    def testLastFmFetch():
        ## Test LastFM retriever
        import lastfmfetch

        lfmr = lastfmfetch.LastFmRetriever(db)
        for artist in lfmr.getAllListenedBands(limit=5):
            db.insertLastFMartists(artist)

    db.close()

