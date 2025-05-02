#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
import threading
from typing import Any, Dict, Generator, Type

from venues.abstract_venue import AbstractVenue, IncorrectVenueImplementation

dbname = "bandevents.db"


def init_db() -> None:
    sql_schema = ""

    with open("schema.sql", mode="r", encoding="utf-8") as f:
        sql_schema = f.readlines()

    with sqlite3.connect(dbname) as conn:
        cur = conn.cursor()
        for stmt in sql_schema:
            cur.execute(stmt)
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

    def pluginCreateVenueEntity(self, venue: Dict[str, str]) -> None:
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
                print(f"Failed with error message: {e}")
            finally:
                cur.close()

    def insertVenueEvents(self, venue: AbstractVenue, events: Dict[str, Any]) -> None:
        """
        Insert parsed events from a venue into the database.
        """
        with self.lock:
            cur = None
            try:
                cur = self.conn.cursor()

                for event in events:
                    venue_id = self.getVenueByName(
                        event["venue"],
                        venue.get_city(),
                        venue.get_country())[0]
                    event["venueid"] = venue_id
                    event.pop("venue")  # venue -> venueid to match sql implementation
                    cols = ", ".join(event.keys())
                    placeholders = ":" + ", :".join(event.keys())
                    q = f"INSERT OR IGNORE INTO event ({cols}) VALUES ({placeholders});"

                    cur.execute(q, event)
            except Exception as e:
                print(f"Failed with error message: {e}")
            finally:
                self.conn.commit()
                cur.close()

    def insertLastFMartists(self, artist: str, playcount: int) -> None:
        q = "INSERT OR REPLACE INTO artist (name, playcount) VALUES (?, ?);"
        with self.lock:
            cur = None
            try:
                cur = self.conn.cursor()
                cur.execute(q, [artist, playcount])
                self.conn.commit()
            except Exception as e:
                print(f"Failed with error message: {e}")
            finally:
                cur.close()

    def getVenues(self) -> Dict[str, str]:
        q = "SELECT id, name, city, country FROM venue"
        cur = None
        results = dict()
        try:
            cur = self.conn.cursor()
            res = cur.conn.execute(q)
            results = res.fetchall()
        except Exception as e:
            print(f"Failed with error message: {e}")
        finally:
            cur.close()

        return results

    def getVenueByName(self, vname: str, city: str, country: str) -> str:
        q = "SELECT id, name, city, country FROM venue " \
            + "WHERE name = ? AND city = ? AND country = ? LIMIT 1;"
        venue_name = str()
        cur = None
        try:
            cur = self.conn.cursor()
            results = cur.execute(q, [vname, city, country])
            venue_name = results.fetchone()
        except Exception as e:
            print(f"Failed with error message: {e}")
        finally:
            cur.close()

        return venue_name

    def getAllGigs(self) -> Dict[str, str]:
        q = "SELECT DISTINCT e.date, v.name, v.city, e.name " \
            + "FROM event AS e INNER JOIN venue AS v ON e.venueid = v.id " \
            + "GROUP BY e.date, v.name ORDER BY e.date ASC;"
        gigs = dict()
        cur = None
        try:
            cur = self.conn.cursor()
            results = cur.execute(q)
            gigs = results.fetchall()
        except Exception as e:
            print(f"Failed with error message: {e}")
        finally:
            cur.close()

        return gigs

    def getArtists(self) -> Generator[Dict[str, str], None, None]:
        q = "SELECT name, playcount FROM artist;"
        cur = None
        try:
            cur = self.conn.cursor()
            results = cur.execute(q)
            for artist, playcount in results.fetchall():
                yield {"artist": artist,
                       "playcount": playcount}
        except Exception as e:
            print(f"Failed with error message: {e}")
        finally:
            cur.close()

    def getArtist(self, name: str) -> Generator[Dict[str, str], None, None]:
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
            print(f"Failed with error message: {e}")
        finally:
            cur.close()

    def purgeOldEvents(self) -> None:
        q = "DELETE FROM event " \
            + "WHERE strftime('%Y-%m-%d', date) < date('now');"
        with self.lock:
            cur = None
            try:
                cur = self.conn.cursor()
                cur.execute(q)
                self.conn.commit()
            except Exception as e:
                print(f"Failed with error message: {e}")
            finally:
                cur.close()
