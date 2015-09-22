# BandEventNotifier
Notify incoming gigs regarding the listened artists on Last.FM.

-- CURRENTLY THIS IS IN BETA VERSION, DON'T EXPECT ANYTHING --


## Motivation
I am a frequent visitor of live music performances.
At times I miss gigs I'd like to see.
Instead of using time to crawl through the venue pages as a weekly
routine and manually parsing all the interesting artist events, it's time to
automate this task.

Last.fm would have been excellent for this but it relies on users creating the
events.
Same applies for Facebook and other sites.
Instead of parsing all the interesting artist sites, I though it would be best
to parse venue programmes only.
I visit cities and countries to see bands, therefore parsing venue sites only
should be sufficient, for now.


## Dependencies
- Python 2.7.x
- Requests
- Sqlite3
- Lxml
- Cssselect
- Pylast
	- API key for Last.fm.


## Setup
Create `APIKEYS` file under the repository and fill it in the following way:

	lastfm username
	lastfm password
	lastfm API key
	lastfm API secret

Database won't get created automatically, yet, and therefore must be created
manually:

	$ sqlite3 bandevents.db < schema.sql

Now, fetch some data and enjoy!

	$ ./bandeventnotifier.py fetch

or to get usage information, just run `./bandeventnotifier.py`.

# LICENSE
Software is BSD Licensed, please see [LICENSE](LICENSE) for more info.

## TODO
- [X] Fetch listening information from last.fm

- [X] Dynamic plugin loader for evenues

- [X] Design database

- [X] Implement threaded fetcher. Initializes plugins (venues) and stores
  fetched events into a database.

- [ ] Style clean ups

- [ ] Maturing and cleaning

## Developer information
### Implementing a new venue parser

=== This section is under construction! ===

BandEventNotifier can be extended with plugins.
Each venue is a plugin.
File `plugin\_handler.py` checks available plugins under `venues/` directory,
and automatically loads everything with a `plugin_` prefix from that directory.
File `bandeventnotifier.py` handles fetching by calling `plugin_\handler.py`
and putting parsed data in to a database.

If one implements an own plugin, it should implement a method called
`parseEvents(data)` which yields the following dict and keys:

	Keys = [u'city', u'country', u'price', u'venue', u'date', u'event']

	Data = {u'city': 'Tampere', u'country': 'Finland', u'price': [u'12e', u'10e'], u'venue': "Dog's home", u'date': u'2015-6-12', u'event': u'A-Fest: Appendix, Korrosive (USA), V\xe4ist\xe4 12\u20ac (ennakko 10\u20ac, tiketti)'}

By using the following construction, it's possible to use an aggregate function of
SQLite to insert data into database.
This method is prepared statement which prevents SQL injections.

When implmenting a plugin, an example plugin `venues/plugin\_dogshome.py` can
be used as a reference.

File name prefix should be `plugin_`, i.e. `plugin_klubi.py`.

### Please follow the following coding conventions:
- Indent is four spaces.
- Line width is maximum 80 chars, really.
- Please use the existing files as a reference.

