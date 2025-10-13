#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
import threading
from typing import Any, Dict, Generator

from venues.abstract_venue import AbstractVenue

dbname = "bandevents.db"


def init_db() -> None:
    sql_schema = """
CREATE TABLE IF NOT EXISTS artist (
	id INTEGER PRIMARY KEY,
	name TEXT NOT NULL UNIQUE,
	playcount INTEGER
);

CREATE TABLE IF NOT EXISTS venue (
	id INTEGER PRIMARY KEY,
	name TEXT NOT NULL,
	city TEXT NOT NULL,
	country TEXT NOT NULL,
	UNIQUE (name, city, country)
);

CREATE TABLE IF NOT EXISTS event (
	id INTEGER PRIMARY KEY,
	name TEXT NOT NULL,
	venueid INTEGER NOT NULL,
	date TEXT NOT NULL,
	price TEXT,
	FOREIGN KEY (venueid) REFERENCES venue(id),
	UNIQUE (name, date, venueid)
);
"""

    with sqlite3.connect(dbname) as conn:
        cur = conn.cursor()
        cur.executescript(sql_schema)
        conn.commit()
        cur.close()


class DBEngine(object):
    def __init__(self) -> None:
        self.conn = None
        self.__first_run()
        self.lock = threading.Lock()

    def __first_run(self) -> None:
        if self.conn is None:
            self.conn = sqlite3.connect(dbname)

    def close(self) -> None:
        with self.lock:
            if self.conn:
                self.conn.close()

    def get_conn(self) -> sqlite3.Connection:
        return self.conn

    def plugin_create_venue_entity(self, venue: Dict[str, str]) -> None:
        """
        Create needed venue entries.

        Parameter venue is Dogshome.eventSQLentity(), i.e.
        """
        cols = ", ".join(venue.keys())
        placeholders = ":" + ", :".join(venue.keys())
        q = "INSERT OR IGNORE INTO venue (%s) VALUES (%s);" \
            % (cols, placeholders)
        with self.lock:
            cur = None
            try:
                cur = self.conn.cursor()
                cur.execute(q, venue)
                self.conn.commit()
            except Exception as e:
                print(f"Couldn't create venue entity: {e}")
            finally:
                cur.close()

    def insert_venue_events(self, venue: AbstractVenue, events: list[dict[str, Any]]) -> None:
        """
        Insert parsed events from a venue into the database.
        """
        with self.lock:
            cur = None
            try:
                cur = self.conn.cursor()

                for event in events:
                    venue_data = self.get_venue_by_name(
                        event["venue"],
                        venue.get_city(),
                        venue.get_country())
                    if venue_data is None:
                        raise f"Couldn't insert events into venue '{venue.name}'"
                    event["venueid"] = venue_data[0]
                    event.pop("venue")  # venue -> venueid to match sql implementation
                    cols = ", ".join(event.keys())
                    placeholders = ":" + ", :".join(event.keys())
                    q = f"INSERT OR IGNORE INTO event ({cols}) VALUES ({placeholders});"
                    cur.execute(q, event)
            except Exception as e:
                print(f"Couldn't insert events for venue '{venue.name}': {e}")
            finally:
                self.conn.commit()
                cur.close()

    def insert_lastfm_artists(self, artist: str, playcount: int) -> None:
        q = "INSERT OR REPLACE INTO artist (name, playcount) VALUES (?, ?);"
        with self.lock:
            cur = None
            try:
                cur = self.conn.cursor()
                cur.execute(q, [artist, playcount])
                self.conn.commit()
            except Exception as e:
                print(f"Couldn't insert artist '{artist}' to LastFM table: {e}")
            finally:
                cur.close()

    def get_venues(self) -> Dict[str, str]:
        q = "SELECT id, name, city, country FROM venue"
        cur = None
        results = dict()
        try:
            cur = self.conn.cursor()
            res = cur.conn.execute(q)
            results = res.fetchall()
        except Exception as e:
            print(f"Couldn't get venue data: {e}")
        finally:
            cur.close()

        return results

    def get_venue_by_name(self, vname: str, city: str, country: str) -> str:
        q = "SELECT id, name, city, country FROM venue " \
            + "WHERE name = ? AND city = ? AND country = ? LIMIT 1;"
        venue_name = str()
        cur = None
        try:
            cur = self.conn.cursor()
            results = cur.execute(q, [vname, city, country])
            venue_name = results.fetchone()
        except Exception as e:
            print(f"Couldn't get venue '{vname}:{city}:{country}' by name: {e}")
        finally:
            cur.close()

        if len(venue_name) != 4:
            raise Exception(f"Wrong number of arguments: {venue_name}")

        return venue_name

    def get_relevant_gigs(self) -> dict[str, str]:
        q = """SELECT
                   e.date,
                   v.name AS venue_name,
                   v.city,
                   e.name AS event_name,
                   GROUP_CONCAT(DISTINCT a.name || ' (' || a.playcount || ')') AS matching_artists
                FROM event AS e
                JOIN venue AS v ON e.venueid = v.id
                JOIN artist AS a
                  ON ' ' || LOWER(REPLACE(REPLACE(e.name, '-', ' '), ':', ' ')) || ' '
                  LIKE '% ' || LOWER(a.name) || ' %'
                WHERE a.playcount > 10
                GROUP BY e.date, v.name, v.city
                ORDER BY e.date ASC;
        """
        gigs = dict()
        cur = None
        try:
            self.conn.row_factory = sqlite3.Row
            cur = self.conn.cursor()
            results = cur.execute(q)
            gigs = results.fetchall()
        except Exception as e:
            print(f"Couldn't get relevant gigs: {e}")
        finally:
            cur.close()

        return gigs

    def get_artists(self) -> Generator[Dict[str, str], None, None]:
        q = "SELECT name, playcount FROM artist;"
        cur = None
        try:
            cur = self.conn.cursor()
            results = cur.execute(q)
            for artist, playcount in results.fetchall():
                yield {"artist": artist,
                       "playcount": playcount}
        except Exception as e:
            print(f"Couldn't get artists: {e}")
        finally:
            cur.close()

    def get_artist(self, name: str) -> Generator[Dict[str, str], None, None]:
        q = "SELECT name, playcount FROM artist " \
            + "WHERE name = ? LIMIT 5;"
        cur = None
        try:
            cur = self.conn.cursor()
            results = cur.execute(q, [name])
            for artist, playcount in results.fetchall():
                yield {"artist": artist,
                       "playcount": playcount}
        except Exception as e:
            print(f"Couldn't get artist '{name}': {e}")
        finally:
            cur.close()

    def purge_old_events(self) -> None:
        q = "DELETE FROM event " \
            + "WHERE strftime('%Y-%m-%d', date) < date('now');"
        with self.lock:
            cur = None
            try:
                cur = self.conn.cursor()
                cur.execute(q)
                self.conn.commit()
            except Exception as e:
                print(f"Couldn't purge old events: {e}")
            finally:
                cur.close()
