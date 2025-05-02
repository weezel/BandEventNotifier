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
Works for me (TM).

## Screenshot

![BandEventNotifier](ben.png)

## Dependencies

- Python 3.x
- Pylast
- requests

## Setup

Install dependencies under `venv` directory by running:

	make install

Setup LastFM credentials by copying `example_lastfm_creds.json` into `lastfm_creds.json` file.
Edit file accordingly, should be self-explanatory.
Obtain API key and secret from https://www.last.fm/api/account/create if needed.

All set! Fetch artists info form LastFM:

	$ ./bandeventnotifier.py fetch --lastfm

or to get usage information, just run `./bandeventnotifier.py`.

## Broken plugin

Venues site layouts changes every now and then.
That means a broken plugin.
One should sacrifice a few minutes to fix the issue but if you are in a hurry,
do the following:
- Check the plugin's file name
- Add broken plugin's file name into `plugin_handler.py` file
- Variable is called `blacklisted`
- i.e. `blacklisted = ["plugin_venuename"]`
- Run the fetch again

Sometimes the domain dies and the plugin handler will go bonkers.
In that case, remove all the `*.pickle` files from `venues/` directory and
blacklist (and delete) the plugin.

If you are not capable to fix the plugin by yourself, please contact the author
of the plugin or me.

# LICENSE
Software is BSD Licensed, please see [LICENSE](LICENSE) for more info.
