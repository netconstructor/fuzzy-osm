#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
from lxml import etree
from bz2 import BZ2File
from osmedit import *

reload(sys)
sys.setdefaultencoding("utf-8")          # a hack to support UTF-8 

try:
  import psyco
  psyco.full()
except ImportError:
  pass

def main ():
  nodes_to_ways = {}
  ways_to_nodes = {}
  way_groups = {}
  graphs = {
  "trunk":set(["motorway","motorway_link","trunk", "trunk_link"]),
  "primary":set(["motorway","motorway_link","trunk", "trunk_link","primary","primary_link"]),
  "secondary":set(["motorway","motorway_link","trunk", "trunk_link","primary","primary_link", "secondary", "secondary_link"]),
  "tertiary":set(["motorway","motorway_link","trunk", "trunk_link","primary","primary_link", "secondary", "secondary_link","tertiary","tertiary_link"]),
  "roads":set(["motorway","motorway_link","trunk", "trunk_link","primary","primary_link", "secondary", "secondary_link","tertiary","tertiary_link","unclassified","road"]),
  }
  for group in graphs:
    way_groups[group] = {}


  osm_infile = BZ2File(sys.argv[1])
  nodes = {}
  nd = []
  curway = []
  tags = {}
  context = etree.iterparse(osm_infile)
  nodes_out = set()
  nodes_needed = set()
  ways_out = set()

  def xml_escape(a):
    a = [b.replace('"',"&quot;") for b in a]
    a = [b.replace('<',"&lt;") for b in a]
    a = [b.replace('>',"&gt;") for b in a]
    return tuple(a)
  for action, elem in context:
    items = dict(elem.items())
    if elem.tag == "tag":
      tags[items["k"]] = items["v"]
    elif elem.tag == "nd":
      nd.append(int(items["ref"]))
    elif elem.tag == "way":
      wid = int(items["id"])
      if "highway" in tags:
        #for node in nd:
          #if node in nodes_to_ways:
            #nodes_to_ways[node].add(wid)
          #else:
            #nodes_to_ways[node] = set([wid])
        #ways_to_nodes[wid] = set(nd)
        for group in graphs:
          if tags["highway"] in graphs[group]:
            way_groups[group][wid] = frozenset(nd)
      tags = {}
      nd = []
    elem.clear()
  #nodes_to_ways_o = nodes_to_ways.deepcopy()
  #ways_to_nodes_o = ways_to_nodes.deepcopy()
  for group in way_groups:
    f = open("graph-%s.html"%group,"w")
    f.write("<html><head><title>%s</title></head><body><table width='100%%'>"%group)
    wg = way_groups[group]
    wgk = set(wg.keys())
     
    while wgk:
       z = wgk.pop()
       cg = set([z])
       cgt = set([z])
       while cgt:
         k = cgt.pop()
         wgkl = wgk.copy()
         while wgkl:
          kl = wgkl.pop()
          if not wg[k].isdisjoint(wg[kl]):
            cg.add(kl)
            cgt.add(kl)
            wgk.discard(kl)
       f.write("<tr><td>%s</td><td><a href='http://openstreetmap.org/browse/way/%s'>%s</a></td></tr>"%(len(cg),z,z))
       print group, cg, len(cg)
    f.write("</table></body></html>")
    f.close()

main()
