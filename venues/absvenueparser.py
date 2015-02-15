# -*- coding: utf-8 -*-

"""
All site parsers should implement this class so they conform the following
format:
    Date (Y-dd-mm) - Artist(s) - Venue

Be sure to parse ';' chars off since that is used as a delimiter later by the
program.
"""

import abc
import datetime
import feedparser
import time


class AbsVenueParser(object):
    __metaclass__ = abc.ABCMeta

    def __init__(cls):
        cls.artists = list()
        cls.venue = str()
        cls.url = str()
        cls.status_code = 0

    #def __repr__(cls):
    #    return "%s: %d events" % (cls.venue, len(cls.artists))

    @abc.abstractmethod
    def parseArtists(self, data):
        pass

