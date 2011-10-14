#!/usr/bin/env python
# -*- coding: utf-8 -*-

from rulesets import Memoize


@Memoize
def NicifyTags(obj="node", oid=0, tags={}, country = ("",), need_review = False):
  if "bridge" in tags:
    tags['bridge'] = tags['bridge'].strip().strip('!')
    if tags.get('bridge', '').lower() in ('мост', 'ponte', 'bridge', 'generic_bridge', 'generic bridge', 'puente'):
      tags['bridge'] = "yes"
    if tags.get('bridge', '').lower() in ('foot', 'footbridge', 'footway', 'path', 'pedestrian', 'foot bridge', 'fußgängerbrücke'):
      if "foot" not in tags:
        tags["foot"] = "yes"
      if "highway" not in tags:
        tags["highway"] = "footway"
      tags["bridge"] = "foot"
    if tags.get('bridge', '').lower() in ('residential', 'track', 'primary', 'unclassified', 'trunk_link', 'road', 'ford', 'bridleway'):
      tags["bridge"] = "yes"
      tags["highway"] = tags.get('highway', tags.get('bridge', '')).lower()
    if tags.get('bridge', '').lower() in ('causway', 'causeway'):
      tags["bridge"] = "causeway"
    if tags.get('bridge', '').lower() in ('suspension','suspended', 'suspensioin'):
      tags["bridge"] = "suspension"
    if tags.get('bridge', '').lower() in ('in planung',):
      tags["bridge"] = "proposed"
    if tags.get('bridge', '').lower() in ('no','bridge_no'):
      tags["bridge"] = "no"
    if tags.get('bridge', '').lower() in ('pantoon','pontoon', 'pont', 'floating', 'panton', 'floating_bridge'):
      tags["bridge"] = "pontoon"
    if tags.get('bridge', '').lower() in ('aqueduct','aqueduc','aquaduct','aquaeduct'):
      tags["bridge"] = "aqueduct"
    if tags.get('bridge', '').lower() in ('viaduct','viadute'):
      tags["bridge"] = "viaduct"
    if tags.get('bridge', '').lower() in ('bailey bridge','bailey'):
      tags["bridge"] = "bailey"
    if tags.get('bridge', '').lower() in ('pipe','pipeline','труба'):
      tags["bridge"] = "pipe"
    if tags.get('bridge', '').lower() in ('бревно','log','деревянный мост','wood','wooden', 'wooden bridge', 'tree_trunks'):
      tags["bridge"] = "yes"
      tags["material"] = 'wood'
    if tags.get('bridge', '').lower() in ('lift','lifting', 'lift_bridge', 'lifting bridge', 'elevator'):
      tags["bridge"] = "lift"
    if tags.get('bridge', '').lower() in ('destroyed','collapsed', 'destructed', 'разрушен', 'missing', 'demolished', 'former'):
      tags["bridge"] = "destroyed"
    if tags.get('bridge', '').lower() in ('swing','yes/swing', 'yes;swing'):
      tags["bridge"] = "swing"
    if tags.get('bridge', '').lower() in ('covered', 'couvert'):
      tags["bridge"] = "covered"
    if tags.get('bridge', '').lower() in ('pier', 'piers'):
      tags["bridge"] = "pier"
    if tags.get('bridge', '').lower() in ('layer1','layer'):
      tags["bridge"] = "yes"
      tags["layer"] = "1"
    if tags.get('bridge', '').lower() in ('bing','yahoo','bing maps'):
      tags["source"] = tags["bridge"]
      tags["bridge"] = "yes"

    if tags.get('bridge', 'yes') not in ('yes', 'viaduct', 'no', 'aqueduct', 'suspension', 'swing', 'abandoned', 'bascule', 'culvert', 'construction', 'foot', 'causeway', 'moveable', 'bailey', 'broken', 'proposed', 'lift', 'pontoon', 'historic', 'arch', 'undefined', 'destroyed', 'covered', ):
      need_review = True
  return need_review, tags