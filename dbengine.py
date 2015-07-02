#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sqlite3

dbname = "bandevents.db"


class DBEngine(object):
    def __init__(self):
        self.conn = None
        self.cur = None
        self.__firstrun()

    def __firstrun(self):
        self.conn = sqlite3.connect(dbname)
        self.cur = self.conn.cursor()

    def close(self):
        if self.cur:
            self.cur.close()
        if self.conn:
            self.conn.close()

    def plugin_create_venue_entity(self, venueaggr):
        """
        Create needed venue entries.

        Parameter venueaggr is Dogshome.eventSQLentity(), i.e.
        """
        cols = ", ".join(venueaggr.keys())
        placeholders = ":" + ", :".join(venueaggr.keys())
        q = u"INSERT OR IGNORE INTO venue (%s) VALUES (%s);" \
                % (cols, placeholders)
        self.cur.execute(q, venueaggr)
        self.conn.commit()

    def getVenues(self):
        q = u"SELECT vid, name, city, country FROM venue"
        results = self.cur.execute(q)
        return results.fetchall()

if __name__ == '__main__':
    import venues.plugin_dogshome

    db = DBEngine()
    doggari = venues.plugin_dogshome.Dogshome()

    db.plugin_create_venue_entity(doggari.eventSQLentity())
    print db.getVenues()

    db.close()

