# BandEventNotifier
Notify incoming gigs regarding the listened artists on Last.FM.

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

## Screenshot
![BandEventNotifier](ben.png)


## Dependencies
- Python 2.7.x
- Requests
- Sqlite3
- Lxml
- Pylast (optional)
	- API key for Last.fm (This isn't needed anymore. Will do the code
	  adjusments in the near future)


## Setup
Create `APIKEYS` file under the repository and fill it in the following way:

	lastfm username
	lastfm password
	lastfm API key
	lastfm API secret

or alternatively just a username:

	my-lastfm-name

Database won't get created automatically, yet, and therefore must be created
manually:

	$ sqlite3 bandevents.db < schema.sql

Now, fetch some data and enjoy!

	$ ./bandeventnotifier.py fetch

or to get usage information, just run `./bandeventnotifier.py`.

# LICENSE
Software is BSD Licensed, please see [LICENSE](LICENSE) for more info.

## TODO
- [ ] Sort plugins by Country/City/venuename

- [ ] Be more verbose when fetching data

- [ ] Improve (dev) documentation

- [X] Better error handling for plugins

- [X] Fetch listening information from last.fm

- [X] Dynamic plugin loader for evenues

- [X] Design database

- [X] Implement threaded fetcher. Initializes plugins (venues) and stores
  fetched events into a database.

