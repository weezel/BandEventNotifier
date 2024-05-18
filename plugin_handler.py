# -*- coding: utf-8 -*-

# Execute this file to see what plugins will be loaded.

# Implementation leans to Lex Toumbourou's example:
# https://lextoumbourou.com/blog/posts/dynamically-loading-modules-and-classes-in-python/

import os
import pkgutil
import sys
from typing import List

from venues.abstract_venue import AbstractVenue


def load_venue_plugins() -> List[AbstractVenue]:
    """
    Read plugin directory and load found plugins.
    Variable "blocklist" can be used to exclude loading certain plugins.
    """
    blocklist = ["plugin_tiketti", "plugin_telakka"]
    found_blocked = list()
    loadedplugins = list()
    pluginspathabs = os.path.join(os.path.dirname(__file__), "venues")

    for loader, plugname, ispkg in \
            pkgutil.iter_modules(path=[pluginspathabs]):
        if plugname in sys.modules or plugname == "abstract_venue":
            continue
        if plugname in blocklist:
            found_blocked.append(plugname.lstrip("plugin_"))
            continue

        plugpath = f"venues.{plugname}"
        loadplug = __import__(plugpath, fromlist=[plugname])

        classname = plugname.split("_")[1].title()
        loadedclass = getattr(loadplug, classname)

        instance = loadedclass()
        loadedplugins.append(instance)
        print(f"Loaded plugin: {instance.get_venue_name()}")
    print("Blocked plugins: {}.\n".format(", ".join(found_blocked[1:])))
    return loadedplugins
