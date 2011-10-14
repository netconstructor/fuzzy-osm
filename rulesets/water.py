#!/usr/bin/env python
# -*- coding: utf-8 -*-

def NicifyTags(obj="node", oid=0, tags={}, country = ("",), need_review = False):
  """
  This ruleset moves everythong to water=* scheme, and does other various cleanups for water. 
  """
  if tags.get("natural","") == "water":
    if tags.get("name","").lower() in ("ezers", "озеро", "lake"):
      if tags.get("water","lake").lower() == 'lake':
        del tags["name"]
        tags["water"] = "lake"
      else:
        need_review = True
    if tags.get("name","").lower() in ("пруд", "pond"):
      if tags.get("water","pond").lower() == 'pond':
        del tags["name"]
        tags["water"] = "pond"
      else:
        need_review = True
    if ("ezers" in tags.get("name","").lower() or "озеро" in tags.get("name","").lower()) and not "water" in tags:
      tags["water"] = "lake"
    if ("пруд" in tags.get("name","").lower() or "pond" in tags.get("name","").lower()) and not "water" in tags:
      tags["water"] = "pond"

  if "waterway" in tags:
    if tags.get("name","").lower() in ("canal", "kanal", "канал"):
      tags["waterway"] = "canal"
      del tags["name"]

  if "waterway" in tags and "natural" in tags:
    if tags["waterway"] == "riverbank" and tags["natural"]=="water":
      tags["water"] = "riverbank"
  if tags.get("landuse","") in ("reservoir", "basin"):
    del tags["landuse"]
    tags["natural"] = "water"
    tags["water"] = "reservoir"
  if tags.get("natural","") == "marsh":
    tags["natural"] = "wetland"
    tags["wetland"] = "marsh"

  return need_review, tags