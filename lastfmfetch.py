#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import threading
from queue import Queue
from typing import Tuple, Generator, List

import lxml.html
import requests

filename = "USERNAME"


class LfmUserError(Exception): pass


class LfmException(Exception): pass


def isEmpty(s):
    return True if s is None or len(s) == 0 else False


class LastFmRetriever(threading.Thread):
    def __init__(self, queue, all_bands):
        threading.Thread.__init__(self)
        self.__queue = queue

        self.artists_playcounts = all_bands
        self.__username = self.__readUsername(filename)
        self.url = "https://www.last.fm/user/{username}/library/artists?page={pagenumber}"

    def __readUsername(self, fname):
        """
        First line of the file must include a username.
        """
        data = list()

        with open(fname, mode="r", encoding="utf-8") as f:
            for line in f:
                data.append(line.replace("\n", ""))

        if len(data) == 1:
            return data[0]

    # FIXME Add venue type
    def calculatePopularity(self, allbands, thisband):
        totalplaycount = sum([int(artist.playcount) for artist in allbands])
        return thisband.playcount / totalplaycount * 100.0

    def getPaginatedPages(self) -> List[str]:
        """
        Returns a list of LastFM library pages. For example:
        [http://www.last.fm/user/exampleUser/library/artists?page=1
         http://www.last.fm/user/exampleUser/library/artists?page=2
         http://www.last.fm/user/exampleUser/library/artists?page=3]
        """
        html = requests.get(self.url.format(
            username=self.__username,
            pagenumber=1))
        site = lxml.html.fromstring(html.content)

        pagestag = site.xpath(
            '//li[contains(@class, " pagination-page")]' +
            '/a/text()')
        pagescount = max([int(i) for i in pagestag], key=lambda i: int(i))
        return [self.url.format(username=self.__username, pagenumber=i)
                for i in range(1, pagescount + 1)]

    def __parsePage(self, html: str) -> None:
        pat_numbers = re.compile("[0-9,]+")
        site = lxml.html.fromstring(html)

        for libitem in site.xpath('//table[contains(@class, "chartlist")]/tbody/tr[contains(@class, "chartlist-row")]'):
            artist = libitem.xpath('./td[contains(@class, "chartlist-name")]/a/text()')
            artist = " ".join(artist).strip()

            parsed_playcount = libitem.xpath(
                './td[contains(@class, "chartlist-bar")]/span/a/span[contains(@class, "chartlist-count-bar-value")]/text()')
            parsed_playcount = " ".join(parsed_playcount)
            playcount = re.search(pat_numbers, parsed_playcount)
            playcount = playcount.group().replace(",", "")

            if isEmpty(artist) or isEmpty(playcount):
                raise LfmException(f"Failed to parse artist ({artist}) or playcount ({playcount})")

            self.artists_playcounts[artist] = int(playcount)

    def getArtistsPlaycounts(self) -> Generator[Tuple[str, int], None, None]:
        for k, v in self.artists_playcounts.items():
            yield k, int(v)

    def __fetch(self, url: str) -> str:
        print(f"Getting data from: {url}", end="\r")
        reply = requests.get(url)
        if not reply.ok:
            print(f"Couldn't fetch data from URL: {url}")
            return ""
        print(f"Completed fetching on {url}")
        return reply.content

    def run(self) -> None:
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
