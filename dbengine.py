#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
import threading
from typing import Dict, Generator

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
        while True:
            with self.lock:
                if self.conn:
                    self.conn.close()
                break

    def pluginCreateVenueEntity(self, venue: Dict[str, str]) -> None:
        """
        Create needed venue entries.

        Parameter venue is Dogshome.eventSQLentity(), i.e.
        """
        cols = ", ".join(venue.keys())
        placeholders = ":" + ", :".join(venue.keys())
        q = "INSERT OR IGNORE INTO venue (%s) VALUES (%s);" \
            % (cols, placeholders)
        while True:
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
                    break

    # FIXME Create a proper venue interface
    def insertVenueEvents(self, venue) -> None:
        """
        Insert parsed events from a venue into the database.
        """
        while True:
            with self.lock:
                # Replace venue by venueid
                venue["venueid"] = self.getVenueByName(venue["venue"])[0]
                # TODO Why do we have this keyword in the dict in general...
                venue.pop("venue")  # No such column in SQL db
                cols = ", ".join(venue.keys())
                placeholders = ":" + ", :".join(venue.keys())
                q = "INSERT OR IGNORE INTO event (%s) VALUES (%s);" \
                    % (cols, placeholders)
                cur = None
                try:
                    cur = self.conn.cursor()
                    cur.execute(q, venue)
                    self.conn.commit()
                except Exception as e:
                    print(f"Failed with error message: {e}")
                finally:
                    cur.close()
                    break

    def insertLastFMartists(self, artist: str, playcount: int) -> None:
        q = "INSERT OR REPLACE INTO artist (name, playcount) VALUES (?, ?);"
        while True:
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
                    break

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

    def getVenueByName(self, vname: str) -> str:
        q = "SELECT id, name, city, country FROM venue " \
            + "WHERE name = ? LIMIT 1;"
        venue_name = str()
        cur = None
        try:
            cur = self.conn.cursor()
            results = cur.execute(q, [vname])
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
        while True:
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
                    break
