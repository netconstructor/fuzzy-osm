#!/usr/bin/env python
# -*- coding: utf-8 -*-

garbage_values = frozenset([".", "-", ",", "", "(", "-)", "()", "FIXME", "t", "?"])

def NicifyTags(obj="node", oid=0, tags={}, country = ("",), need_review = False):
  """
  This ruleset drops tags that are import garbage or other kind of it.
  """
  for i in ('building', 'landuse', 'natural'):
    if i in tags and "area" in tags:
      del tags[i]  

  # Created when transforming GPX waypoints into nodes
  if "wpt_description" in tags and "wpt_symbol" in tags:
    del tags["wpt_description"]
    del tags["wpt_symbol"]

  # broken mp2osm converters leave a lot of these
  if tags.get('Type', '').lower() in ('0x13', '0x6c', '0x6', '0x6f', '0xb'):
    del tags['Type']    
  
  # some people fill tags with fake values
  if "place" in tags:
    for ntag in ("name:ru", "name", "name:en", "addr:postcode", "cladr:name", "int_name"):
      if ntag in tags and tags.get(ntag).lower() in ("город н", "gorod n", "индекс города н"):
        del tags[ntag]

  for key in tags.keys():
    tags[key] = tags[key].strip()
    if tags[key] in garbage_values:
      del tags[key]

  # potlatch reverts
  if "history" in tags:
    if "etrieved" in tags["history"]:
      del tags["history"]

  # left hanging after an import in Latvia
  if "cat_" in tags:
    del tags["cat_"]

  # landuse=firest natural=wood - early mistake in russian OSM wiki translation that was duplicated a lot
  if "landuse" in tags and "natural" in tags:
    if tags["landuse"]=="forest" and tags["natural"] == "wood":
      del tags["landuse"]

  # people fill a lot of addr:housenumbers with garbage just to satisfy JOSM validator
  if "addr:housenumber" in tags:
    if tags["addr:housenumber"] in ("0", "0?", "00"):
      del tags["addr:housenumber"]

  if "created_by" in tags:
    del tags["created_by"]

  if "converted_by" in tags:
    del tags["converted_by"]

  # a lot of source= on nodes that are duplicated on lines
  if "source" in tags and len(tags)==1 and obj == "node":
    del tags["source"]
  return need_review, tags