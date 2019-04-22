#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import threading
from queue import Queue

import lxml.html
import requests


FNAME = "USERNAME"


class LfmUserError(Exception): pass

class LastFmRetriever(threading.Thread):
    def __init__(self, queue, all_bands):
        threading.Thread.__init__(self)
        self.__queue = queue

        self.artists_playcounts = all_bands
        self.__username = self.__readUsername(FNAME)
        self.url = "https://www.last.fm/user/{username}/library/artists?page={pagenumber}"

    def __readUsername(self, fname):
        """
        First line of the file must include a username.
        """
        data = list()

        with open(fname, "r") as f:
            for line in f:
                data.append(line.replace("\n", ""))

        if len(data) == 1:
            return data[0]

    def calculatePopularity(self, allbands, thisband):
        totalplaycount = sum([int(artist.playcount) for artist in allbands])
        return thisband.playcount / totalplaycount * 100.0

    def getPaginatedPages(self):
        """
        Returns a list of LastFM library pages. For example:
        [http://www.last.fm/user/exampleUser/library/artists?page=1
         http://www.last.fm/user/exampleUser/library/artists?page=2
         http://www.last.fm/user/exampleUser/library/artists?page=3]
        """
        pageidx = 1
        html = requests.get(self.url.format(username=self.__username, \
                pagenumber=1))
        site = lxml.html.fromstring(html.content)

        pagestag = site.xpath('//li[contains(@class, " pagination-page")]' + \
                              '/a/text()')
        pagescount = max([int(i) for i in pagestag], key=lambda i: int(i))
        return [self.url.format(username=self.__username, pagenumber=i) \
                for i in range(1, pagescount + 1)]

    def __parsePage(self, html):
        pat_numbers = re.compile("[0-9,]+")

        site = lxml.html.fromstring(html)

        for libitem in site.xpath('//tbody/tr'):
            artist = libitem.xpath('./td[@class="chartlist-name"]/span/a/text()')
            artist = " ".join(artist).strip()

            # Bail early, no need to parse further.
            # Since we use fairly eager matching, LastFM's newest changes
            # hit in this rule too.
            # The mismatch is caused by "Listening History" charts.
            if artist == "":
                continue

            parsed_playcount = libitem.xpath('./td[@class="chartlist-countbar"]' \
                                    + '/span/span/a/span/text()')
            parsed_playcount = " ".join(parsed_playcount)
            playcount = re.search(pat_numbers, parsed_playcount)
            playcount = playcount.group().replace(",", "")

            self.artists_playcounts[artist] = int(playcount)

    def getArtistsPlaycounts(self):
        for k, v in self.artists_playcounts.items():
            yield k, v

    def __fetch(self, url):
        print(f"Getting data from: {url}", end="\r")
        reply = requests.get(url)
        if not reply.ok:
            print(f"Couldn't fetch data from URL: {url}")
            return
        print(f"Completed fetching on {url}")
        return reply.content

    def run(self):
        while True:
            url = self.__queue.get()
            html = self.__fetch(url)
            self.__parsePage(html)
            self.__queue.task_done()

if __name__ == '__main__':
    lfmQueue = Queue()
    all_bands = dict()
    lfmr = LastFmRetriever(lfmQueue, all_bands)

    pages = lfmr.getPaginatedPages()

    for v in range(25):
        t = LastFmRetriever(lfmQueue, all_bands)
        t.setDaemon(True)
        t.start()
    for page in pages:
        lfmQueue.put(page)
    lfmQueue.join()

    print("# [Rank] Playcount: Artist")
    for i, kv in enumerate(sorted(lfmr.getArtistsPlaycounts(),
                                  key=lambda x: x[1],
                                  reverse=True)):
        print(f"[{i:>6d}] {kv[1]:>6d}: {kv[0]}")

