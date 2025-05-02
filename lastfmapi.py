import sqlite3
from concurrent.futures import ThreadPoolExecutor
from itertools import islice
from typing import Generator, Iterable

import pylast


# Obtain API key and secret from https://www.last.fm/api/account/create
class LastFMFetcher:
    def __init__(
            self,
            username: str,
            password: str,
            api_key: str,
            api_secret: str,
    ) -> None:
        self.network = pylast.LastFMNetwork(
            username=username,
            password_hash=pylast.md5(password),
            api_key=api_key,
            api_secret=api_secret,
        )

    def fetch_and_store_all_artists(self, db_conn: sqlite3.Connection) -> None:
        """
        fetch_and_store_all_artists gets all artists from Last.FM and stores
        them into the database. Fetching utilizes parallerization and items
        are stored in chunks.
        """
        my_lib = self.network.get_authenticated_user().get_library()

        # TODO This returns a generator but there's still something off because
        #      it doesn't print the progress nor write to database during the fetch.
        #      Isolated code snippet with no Pylast calls works as intended.
        artists = my_lib.get_artists(limit=0, stream=True)

        def artist_info(artist_item: pylast.Artist) -> (str, int):
            try:
                artist, playcount, _ = artist_item
                print(f"Found artist: {artist.name}")  # TODO Remove this once progress printing works
                return artist.name, playcount
            except Exception as e:
                print("Error in handle_artist:", e, flush=True)
                return None

        def batch(iterable: Iterable, size: int) -> Generator[Iterable, int]:
            """Batch an iterable into chunks of size"""
            it = iter(iterable)
            while chunk := list(islice(it, size)):
                yield chunk

        cursor = db_conn.cursor()
        with ThreadPoolExecutor(max_workers=8) as executor:
            processed_artists = filter(
                None,
                executor.map(
                    artist_info,
                    artists,
                    chunksize=10,
                ),
            )

            # Insert into database in the given chunk sizes.
            for chunk in batch(processed_artists, size=20):
                cursor.executemany("INSERT OR IGNORE INTO artist (name, playcount) VALUES (?, ?)", chunk)
                db_conn.commit()
