CREATE TABLE IF NOT EXISTS artist
(
	bid INTEGER PRIMARY KEY,
	name TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS venue
(
	vid INTEGER PRIMARY KEY,
	name TEXT NOT NULL,
	city TEXT NOT NULL,
	country TEXT NOT NULL,
	UNIQUE (name, city, country)
);

CREATE TABLE IF NOT EXISTS event
(
	eid INTEGER PRIMARY KEY,
	artistid INTEGER NOT NULL,
	venueid INTEGER NOT NULL,
	dateid INTEGER NOT NULL,
	cityid INTEGER NOT NULL,
	FOREIGN KEY (artistid) REFERENCES artist(bid),
	FOREIGN KEY (venueid) REFERENCES venue(vid),
	FOREIGN KEY (dateid) REFERENCES vanue(date),
	FOREIGN KEY (cityid) REFERENCES event(eid),
	UNIQUE (artistid, dateid, venueid)
);

