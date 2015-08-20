# -*- coding: utf-8 -*-

# Execute this file to see what plugins will be loaded.

# Implementation leans to Lex Toumbourou's example:
# https://lextoumbourou.com/blog/posts/dynamically-loading-modules-and-classes-in-python/

import os
import pkgutil
import sys


def load_venue_plugins():
    """
    Read plugin directory and load found plugins.
    Variable "blacklisted" can be used to exclude loading certain plugins.
    """
    blacklisted = ["plugin_klubi", "plugin_pakkahuone", "plugin_tiketti", \
                   "plugin_vastavirta"]
    foundblacklisted = list()
    loadedplugins = list()
    pluginspathabs = os.path.join(os.path.dirname(__file__), "venues")

    for loader, plugname, ispkg in \
            pkgutil.iter_modules(path = [pluginspathabs]):
        if plugname in sys.modules:
            continue
        if plugname in blacklisted:
            foundblacklisted.append(plugname.lstrip("plugin_"))
            continue

        plugpath = "venues.%s" % (plugname)
        loadplug = __import__(plugpath, fromlist = [plugname])

        classname = plugname.split("_")[1].title()
        loadedclass = getattr(loadplug, classname)

        instance = loadedclass()
        loadedplugins.append(instance)
        print "Loaded plugin: %s" % instance.getVenueName()
    print "Blacklisted plugins: %s.\n" % (", ".join(foundblacklisted[1:]))
    return  loadedplugins

if __name__ == '__main__':
    load_venue_plugins()
