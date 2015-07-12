#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sqlite3

dbname = "bandevents.db"


class DBEngine(object):
    def __init__(self):
        self.conn = None
        self.cur = None
        self.__firstrun()
        self.venues = dict()

    def __firstrun(self):
        self.conn = sqlite3.connect(dbname)
        self.cur = self.conn.cursor()

    def close(self):
        if self.cur:
            self.cur.close()
        if self.conn:
            self.conn.close()

    def plugin_create_venue_entity(self, venuedict):
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

    def insert_venue_events(self, venueaggr):
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
            self.conn.commit()

    def get_venues(self):
        q = u"SELECT id, name, city, country FROM venue"
        results = self.cur.execute(q)
        return results.fetchall()

    def get_venue_by_name(self, vname):
        q = u"SELECT id, name, city, country FROM venue " \
           + "WHERE name = ? LIMIT 1;"
        results = self.cur.execute(q, [vname])
        return results.fetchone()

if __name__ == '__main__':
    import venues.plugin_dogshome

    db = DBEngine()
    doggari = venues.plugin_dogshome.Dogshome()

    db.plugin_create_venue_entity(doggari.eventSQLentity())
    print db.get_venues()
    print db.get_venue_by_name("Dog's home")
    print db.get_venue_by_name("Testijuottola that should fail")
    print
    db.insert_venue_events(doggari.parse_events(""))

    db.close()

