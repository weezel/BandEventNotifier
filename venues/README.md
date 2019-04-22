# Developer information

### Implementing a new venue parser (plugin)

BandEventNotifier can be extended with plugins.
Each venue is a plugin.
File `plugin_handler.py` checks available plugins under `venues/` directory,
and loads automatically everything with a `plugin_` prefix from that directory.
File `bandeventnotifier.py` handles fetching by calling `plugin_handler.py`
and putting parsed data in to a database.

Python's SQLite implementation has problems with concurrent connections and
therefore the current approach is a hack.
To overcome this limitation SQLalchemy should be used.

## Abstract methods
When creating a new plugin class, it must have the following attributes set:

	self.url = str()
	self.name = str()
	self.city = str()
	self.country = str()

Plugin must implement `parseEvents(data)` method.
The method must yield the following keys:

	Keys = ['venue', 'date', 'name', 'price']

Which eventually will look something like this:

	KEY         VALUE
	-----------------
	date      : 2015-12-12
	price     : 6€
	venue     : Dog's home
	name      : Nem-klubi: Simulacrum, Masterstroke 6€

## Format of values
A word about the values.

* Date must be in `%Y-%m-%d` format.

* Price must be in `[0-9.]+/?([0-9.]+)?€` format. If there is cheaper price for
  pre-orders, that must be the first value.
  The latter value is when the ticket is bought from a door.
  Dash is a separator.
  Single values should be in `[0-9.]€` format.

* Venue is the venue's full name.

* Name is the event name, can include descriptions and title.

By using the following structure, it's possible to use an aggregate function for
SQLite to insert data into the database.
This method uses prepared statements, which prevents SQL injections - at least
in some level.

Plugins under `venues/` directory can be used as a reference when implementing
a new plugin.

File name prefix should be `plugin_`, i.e. `plugin_klubi.py`.

## Temporarily disabling plugins
If for a reason or an another one must disable a plugin temporarily, it can be
added to `blacklisted` list which in `plugin_handler.py` file.

### Coding rules
- Indent is four spaces.
- Line width is maximum 80 chars
- Please use the existing files as a reference.

