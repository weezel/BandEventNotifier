# -*- coding: utf-8 -*-


class Artist():
    def __init__(self, date, name, venue):
        self.date = date
        self.name = name
        self.venue = venue

    def getTriplet(self):
        return "%s;%s;%s" % (self.date, self.name, self.venue)

    def __repr__(self):
        return getTriplet()

