#!/usr/bin/env python
# -*- coding: utf-8 -*-

def NicifyTags(obj="node", oid=0, tags={}, country = ("",), need_review = False):
  """
  This ruleset drope names that describe the type of object and are pointless.
  """
  if tags.get("amenity","") == "cafe":
    if tags.get("name","").lower().strip() in ("кафе","cafe"):
      del tags["name"]
    if tags.get("name:ru","").lower().strip() in ("кафе","cafe"):
      del tags["name:ru"]

  if tags.get("leisure","") == "stadium":                                    ## школьные "стадионы" - это просто площадки
    if tags.get("name","").lower().strip() in ("школьный стадион",):
      tags["leisure"] = "pitch"
    if tags.get("name","").lower().strip() in ("стадион", "школьный стадион"):
      del tags["name"]
    if tags.get("name:ru","").lower().strip() in ("стадион", "школьный стадион"):
      del tags["name:ru"]

  if tags.get("landuse","") == "construction":
    if tags.get("name","").lower().strip() in ("стройка", "строительство", "стр-во"):
      del tags["name"]

  if tags.get("amenity","") == "recycling":
    if "мусорка" in tags.get("name","").lower():
      tags["amenity"] = "waste_basket"
      del tags["name"]

  if tags.get("amenity","") == "school":
    if "name" in tags:
      name = tags["name"].lower()
      if name in ("школа", 'school', 'школа №'):
        del tags["name"]

  if tags.get("shop","")=="car":
    if tags.get("name","").lower()=="сто" or tags.get("name","").lower()=="сто (sto)":
      del tags["name"]
      tags["shop"] = "car_repair"
      if tags.get("name:ru","").lower()=="сто":
        del tags["name:ru"]
      if tags.get("name:be","").lower()=="ста":
        del tags["name:be"]  
    if u"сто" in tags.get("name","").lower():
      tags["shop"] = "car_repair"
  return need_review, tags