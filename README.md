# BandEventNotifier
Notify incoming gigs regarding the listened artists in Last.FM.

-- CURRENTLY THIS IS IN DELTA VERSION, DON'T EXPECT ANYTHING --

## Motivation
I am a frequent visitor of live music performances. At times I miss gigs I'd
like to see. Instead of using time to crawl through the venue pages as a weekly
basis and manually parsing all the interesting artist events, it's time to
automate this task.

## Dependencies
- Python 2.7.x
- Requests
- Sqlite3
- Lxml
- Pylast

# LICENSE
Software is BSD Licensed, please see `LICENSE` for more info.

## TODO
- [X] Fetch listening information from last.fm

- [X] Dynamic plugin loader for evenues

- [ ] Design database

- [ ] Implement threaded fetcher. Initializes plugins (venues) and stores
  fetched events into a database.

## Developer information
### Implementing a new venue parser
When implementing a new venue parser, here's a quick start:

- Implement methods shown in `absvenueparser.py` abstract class.

- File name prefix should be `plugin_`, i.e. `plugin_klubi.py`.

### Please follow the following coding conventions:
- Indent is four spaces.
- Line width is maximum 80 chars, really.
- Please see the existing files for reference.

## Constraints for database
There are many bands
There are many venues

Venues can have many bands
A band can have many gigs in different venues
A band can have many gigs in the same venue

There can be many bands with the same name

