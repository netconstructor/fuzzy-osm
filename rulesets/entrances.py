#!/usr/bin/env python
# -*- coding: utf-8 -*-

def NicifyTags(obj="node", oid=0, tags={}, country = ("",), need_review = False):
  if tags.get("building", '').lower() in ('main_entrance', 'public_entrance', 'station_entrance'):
    tags["entrance"] = "main"
    del tags['building']
  if tags.get("building", '').lower() in ('garage_entrance',):
    tags["entrance"] = "garage"
    del tags['building']
  if tags.get("building", '').lower() in ('emergency_exit',):
    tags["entrance"] = "emergency"
    del tags['building']

  for t in ('enterance', 'entrace', 'enterace', 'enterence', 'entrace', 'entrence', 'entrance;yes', 'entance', 'entracne', "entrance'", 'enrance', 'buuilding_entrance', "ntrance'", 'eintrance', 'entrnace', 'entry', 'enter'):
    if t in tags:
      tags["entrance"] = tags[t]
      del tags[t]
    if tags.get("building", '').lower() == t and obj == "node":
      if "entrance" not in tags:
        tags["entrance"] = "yes"
      del tags["building"]
  return need_review, tags