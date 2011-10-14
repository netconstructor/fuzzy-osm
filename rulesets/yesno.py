#!/usr/bin/env python
# -*- coding: utf-8 -*-
YES_SPELLING = ("yes", "true", "1", "es", "t", "tr", "zes", "ffcc", "pt", "yed", "^y", "yx", "yr", "y", "y\\", "yes\\", "y#", "yea", "y+", "yes+1", "yµ", "uy", "*", "<", "#", 'e', 'e#')
NO_SPELLING = ('no', 'false', '0')

def NicifyTags(obj="node", oid=0, tags={}, country = ("",), need_review = False):
  for key in ('bridge', 'oneway', 'building', 'entrance', 'area'):
    if tags.get(key,"").lower() in YES_SPELLING:
      tags[key] = "yes"
    if tags.get(key,"").lower() in NO_SPELLING:
      tags[key] = "no"
  return need_review, tags