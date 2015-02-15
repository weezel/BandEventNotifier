# -*- coding: utf-8 -*-

# Implementation leans Lex Toumbourou's example:
# https://lextoumbourou.com/blog/posts/dynamically-loading-modules-and-classes-in-python/

import os
import pkgutil
import re
import sys


def load_venue_plugins():
    """
    Read plugin directory and load found plugins.
    Variable "blacklisted" can be used to exclude loading certain plugins.
    """
    blacklisted = ["absvenueparser", "plugin_klubi", "plugin_tiketti"]
    foundblacklisted = list()
    pluginspathabs = os.path.join(os.path.dirname(__file__), "venues")

    for loader, plugname, ispkg in \
            pkgutil.iter_modules(path = [pluginspathabs]):
        if plugname in sys.modules:
            continue
        if plugname in blacklisted:
            foundblacklisted.append(plugname)
            continue

        plugpath = "%s.%s" % (pluginspathabs, plugname)
        loadplug = __import__(plugpath, fromlist = [plugname])

        classname = plugname.split("_")[1].title()
        loadedclass = getattr(loadplug, classname)

        instance = loadedclass()
        print "Loaded plugin: %s" % instance.getVenue()
    print "Found but blacklisted plugins: %s." % \
           (", ".join(foundblacklisted[1:]))

load_venue_plugins()

