#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
from libtxt2osm import *
from osmedit import *

reload(sys)
sys.setdefaultencoding("utf-8")          # a hack to support UTF-8 

try:
  import psyco
  psyco.full()
except ImportError:
  pass

def main ():
 
  cs = set()
  DROPPED_POINTS = 0
  WAYS_WRITTEN = 0
  NODES_READ = 0
  WAYS_READ = 0
  UNMATCHED = 0
  TOTAL = 0
  infile = open(sys.argv[1])
  nodes = {}
  nd = []
  curway = []
  tags = {}
  
  nodes_out = set()
  nodes_needed = set()
  ways_out = set()
  
  osmcode = open("out.osm","w")
  osmcode.write('<osm version="0.6">')
  #ref_pattern = re.compile(u"([mMpPhHмМрРнНvVaAаАпПeEеЕтТtT])[ -]*(\d+)")
  def xml_escape(a):
    #print a
    a = [b.replace('&',"&amp;") for b in a]
    a = [b.replace('"',"&quot;") for b in a]
    a = [b.replace('<',"&lt;") for b in a]
    a = [b.replace('>',"&gt;") for b in a]    
    return tuple(a)
  id = -1
  for line in infile:
    TOTAL += 1
    id -= 1
    lat = line.split()[0]
    lon = line.split()[1]
    line = " ".join(line.split()[3:])

    
    tags = txt2osmtags(line)
    if "description" in tags:
      print lat, lon, line
      UNMATCHED += 1
    tags["txt2osm:reviewed"]= "no"
    if tags:
        ntags = NicifyTags("node", id, tags)
      #if tags != ntags:
        osmcode.write( '<node id="%s" lon="%s" lat="%s" version="%s" action="modify">\n'%(id, lon, lat, 1))
        ntags = dict([xml_escape(i) for i in ntags.items()])
        for z in ntags.iteritems():
          osmcode.write( '    <tag k="%s" v="%s" />\n'%z)
        osmcode.write( '</node>\n')
        osmcode.flush()
  osmcode.write( '</osm>\n')
  print "%s / %s, %.3f%% matched"%(UNMATCHED, TOTAL, -100.*(UNMATCHED-TOTAL)/TOTAL) 

main()
