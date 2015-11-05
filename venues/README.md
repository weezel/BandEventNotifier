# Developer information
### Implementing a new venue parser (plugin)

BandEventNotifier can be extended with plugins.
Each venue is a plugin.
File `plugin\_handler.py` checks available plugins under `venues/` directory,
and loads automatically everything with a `plugin_` prefix from that directory.
File `bandeventnotifier.py` handles fetching by calling `plugin_\handler.py`
and putting parsed data in to a database.
Python's SQLite implementation has problems with concurrent connections and
therefore the current approach is more like a hack.
To overcome this hack, one must implement a working concurrency handler for
`dbengine.py`.
One approach is to use SQLAlchemy but that adds more dependencies which I'd
like to avoid, and would need a complete rewrite.

## Plugin return values
If one implements an own plugin, it should implement a method called
`parseEvents(data)`, which in example yields the following dict and keys:

	Keys = [u'city', u'country', u'price', u'venue', u'date', u'event']
	KEY         VALUE
	-----------------
	date      : 2015-12-12
	price     : 6€
	venue     : Dog's home
	name      : Nem-klubi: Simulacrum, Masterstroke 6€

A word about the values.

* Date must be in `%Y-%m-%d` format.

* Price must be in `[0-9.]+/?([0-9.]+)?€` format. If there is cheaper price for
  pre-orders, that must be the first value. The latter value is when the ticket
  is bought from a door. Dash is a separator. Single values should be in
  `[0-9.]€` format.

* Venue is the venue's full name.

* Name is the event name, can include descriptions and title.

By using the following structure, it's possible to use an aggregate function for
SQLite to insert data into the database.
This method uses prepared statements, which prevents SQL injections - at least
in some level.

When implmenting a plugin, an example plugin `venues/plugin\_klubi.py` can
be used as a reference.

File name prefix should be `plugin_`, i.e. `plugin_klubi.py`.

### Please follow the following coding conventions:
- Indent is four spaces.
- Line width is maximum 80 chars, really.
- Please use the existing files as a reference.

