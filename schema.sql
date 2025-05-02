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
	UNIQUE (name, city, country),
);

CREATE TABLE IF NOT EXISTS event (
	id INTEGER PRIMARY KEY,
	name TEXT NOT NULL,
	venueid INTEGER NOT NULL,
	date TEXT NOT NULL,
	price TEXT,
	FOREIGN KEY (venueid) REFERENCES venue(id),
	UNIQUE (name, date, venueid),
);

PRAGMA journal_mode=WAL;
