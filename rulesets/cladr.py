#!/usr/bin/env python
# -*- coding: utf-8 -*-

def NicifyTags(obj="node", oid=0, tags={}, country = ("",), need_review = False):
  """
  cladr:* tags were set up by bot and aren't either fully correct or useful
  """
  
  # non-numerical cladr:codes are impossible, thus drop these
  if not tags.get("cladr:code","0").isdigit():
    del tags["cladr:code"]
    if "cladr:suffix" in tags:
      del tags["cladr:suffix"]

  # cladr:code for buildings was onse set up based on addr:street. that's neither correct nor used by anyone.
  if "building" in tags:
    if "cladr:code" in tags:
      del tags["cladr:code"]

  # cladr:name aren't useful too, when they repeat name. If they don't repear name= it's a case for investigation.
  # TODO: add mangler by AMDmi3 for name comparasion
  if "cladr:name" in tags:
    cn = tags["cladr:name"].lower().strip()
    cs = tags.get("cladr:suffix","").lower().strip()
    if tags.get("name","").lower() in (cs+" "+cn, cn+" "+cs, cn):
      del tags["cladr:name"]
      if "cladr:suffix" in tags:
        del tags["cladr:suffix"]
      if "name:ru" not in tags:
        tags["name:ru"] = tags["name"]
    else:
      need_review = True

  return need_review, tags