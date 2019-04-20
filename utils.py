#!/usr/bin/env python3
# -*- coding: utf-8 -*-

def colorize(text, color):
    colors = { "black"     : 30,
               "red"       : 31,
               "green"     : 32,
               "yellow"    : 33,
               "blue"      : 34,
               "purple"    : 35,
               "cyan"      : 36,
               "white"     : 37,
               "bold"      : 1,
               "underline" : 4,
               "blink"     : 5,
               "inverse"   : 6 }
    return "\033[0;0;%dm%s\033[0m" % (colors[color], text)

def levenshtein(word1, word2, distance):
    pass
