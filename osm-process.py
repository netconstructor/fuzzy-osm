#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
from lxml import etree
#from bz2 import BZ2File
from osmedit import *

import subprocess

def osmopen(filename):
  if filename[-3:] == "pbf":
    return subprocess.Popen(['pbf2osm', filename], stdout=subprocess.PIPE, bufsize=1).stdout
    
  if filename[-3:] == "bz2":
    return subprocess.Popen(['bzcat', filename], stdout=subprocess.PIPE, bufsize=1).stdout
  return open(filename, "r")
reload(sys)
sys.setdefaultencoding("utf-8")          # a hack to support UTF-8 

try:
  import psyco
  psyco.full()
except ImportError:
  pass

#def NicifyTags(obj, oid, tags):
  #tags = tags.copy()
  #if "created_by" in tags:
    #del tags["created_by"]
  #return tags

def main ():
 # changes = {}
  cs = set()
  #place_csv = open("expand.csv","r")
  #for line in place_csv:
    #a,b = line.split(",")
    ##print a , b
    #a = unicode(a.strip())
    #b = unicode(b.strip())
    #changes[a] = b
    #cs.add(a)
  #print changes
  DROPPED_POINTS = 0
  WAYS_WRITTEN = 0
  NODES_READ = 0
  WAYS_READ = 0
  osm_infile = osmopen(sys.argv[1])
  nodes = {}
  nd = []
  curway = []
  tags = {}
  context = etree.iterparse(osm_infile)
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
  for action, elem in context:
    items = dict(elem.items())
    if elem.tag == "node":
      if tags:
        ntags = NicifyTags(elem.tag, items["id"], tags)
        if tags != ntags:
          nodes_out.add(items['id'])
          osmcode.write( '<node id="%s" uid="%s" user="%s" changeset="%s" timestamp="%s" lon="%s" lat="%s" version="%s" action="modify">\n'%(items["id"], items.get("uid",0), xml_escape((items.get("user", "unknown"),))[0], items["changeset"], items["timestamp"], items["lon"],items["lat"],items["version"]))
          ntags = dict([xml_escape(i) for i in ntags.items()])
          for z in ntags.iteritems():
            osmcode.write( '    <tag k="%s" v="%s" />\n'%z)
          osmcode.write( '</node>\n')
          osmcode.flush()
      tags = {}
    elif elem.tag == "tag":
      tags[items["k"]] = items["v"]
    elif elem.tag == "nd":
      nd.append(items["ref"])
    elif elem.tag == "way":
      if tags:
        ntags = NicifyTags(elem.tag, items["id"], tags)
        if tags != ntags:
          ways_out.add(items['id'])
          osmcode.write( '<way id="%s" uid="%s" user="%s" timestamp="%s" changeset="%s" version="%s" action="modify">\n'%(items["id"], items.get("uid",0), xml_escape((items.get("user", "unknown"),))[0], items["timestamp"], items["changeset"], items["version"]))
          #osmcode.write( '<way id="%s" version="%s" action="modify">\n'%(items["id"],items["version"]))
          ntags = dict([xml_escape(i) for i in ntags.items()])
          for z in ntags.iteritems():
            osmcode.write( '    <tag k="%s" v="%s" />\n'%z)
          for z in nd:
            osmcode.write( '    <nd ref="%s"/>\n'%z)
          nodes_needed.update(nd)
          osmcode.write( '</way>\n')
          osmcode.flush()        
      tags = {}
      nd = []
    elif elem.tag == "relation":
      break
    elem.clear()
  osm_infile = osmopen(sys.argv[1])
  context = etree.iterparse(osm_infile)
  nodes_needed.difference_update(nodes_out)
  tags = {}
  for action, elem in context:
    items = dict(elem.items())
    if not nodes_needed:
      break
    if elem.tag == "node":
      if items['id'] in nodes_needed and items['id'] not in nodes_out:
        nodes_needed.remove(items['id'])
        nodes_out.add(items['id'])
        osmcode.write( '<node id="%s" uid="%s" user="%s" changeset="%s" timestamp="%s" lon="%s" lat="%s" version="%s">\n'%(items["id"], items.get("uid",0), xml_escape((items.get("user", "unknown"),))[0], items["changeset"], items["timestamp"], items["lon"],items["lat"],items["version"]))
        tags = dict([xml_escape(i) for i in tags.items()])
        for z in tags.iteritems():
          osmcode.write( '    <tag k="%s" v="%s" />\n'%z)
        osmcode.write( '</node>\n')
        osmcode.flush()
      tags = {}
    elif elem.tag == "tag":
      tags[items["k"]] = items["v"]
    elif elem.tag == "nd":
      nd.append(items["ref"])
    elif elem.tag == "way":
      tags = {}
      nd = []
      break
    elem.clear()
  osmcode.write( '</osm>\n')

main()
