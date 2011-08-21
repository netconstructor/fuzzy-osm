#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re

def txt2osmtags (txt):
  tags = {}
  txt = txt.strip()
  txtl = unicode(txt).lower()

  if txtl in ("wc", "toilet", "туалет"):
    tags["amenity"] = "toilets"
  elif txtl in ("аптека", ):
    tags["amenity"] = "pharmacy"
  elif txtl in ("остановка", ):
    tags["highway"] = "bus_stop"
  elif txtl in ("лежекоп", ):
    tags["traffic_calming"] = "bump"
  elif txtl in ("кладбище", ):
    tags["landuse"] = "cemetery"
    tags["fixme:type"] = "area"
  elif txtl in ("суд", ):
    tags["amenity"] = "courthouse"
  elif txtl in ("фонтан", ):
    tags["amenity"] = "fountain"
  elif txtl in ("котельная", ):
    tags["power"] = "generator"
    tags["generator:method"] = "combustion"
  elif txtl in ("гостиница", "отель" ):
    tags["amenity"] = "hotel"
  elif txtl in ("магазин", "продмаг" ):
    tags["shop"] = "convenience"
  elif txtl in ("автосервис", "сто" ):
    tags["shop"] = "car_repair"

  elif txtl in ("автозапчасти",  ):
    tags["shop"] = "car_parts"

  elif txtl in ("обелиск", "монумент" ):
    tags["historic"] = "monument"    
  elif txtl in ("стройматериалы", "магазин стройматериалов" ):
    tags["shop"] = "doityourself"    
  elif txtl in ("школа",  ):
    tags["amenity"] = "school"
  elif txtl in ("детский сад",  ):
    tags["amenity"] = "kindergarten"
  elif txtl in ("пляж",  ):
    tags["amenity"] = "beach"

  elif txtl in ("мтс",  ):
    tags["office"] = "telecommunication"  
    tags["operator"] = "МТС"  

  elif txtl in ("столовая",  ):
    tags["amenity"] = "fast_food"  

  
  elif txtl in ("полигон тбо", "свалка" ):
    tags["landuse"] = "landfill"
    tags["fixme:type"] = "area"

  elif txtl in ("гаражи", "гск" ):
    tags["landuse"] = "garages"
    tags["fixme:type"] = "area"

  elif txtl in ("сад",  ):
    tags["landuse"] = "orchard"
    tags["fixme:type"] = "area"

  elif re.search(r"(ул.|просп.|пер.|бульвар|площадь).*",txt):
    tags["name"] = txt
    tags["highway"] = "road"
    tags["fixme:type"] = "way"

  elif re.search(r"МТФ \"(.*)\"",txt):
    tags["name"] = re.search(r"МТФ \"(.*)\"",txt).groups()[0]
    tags["amenity"] = "farm"
    tags["farm"] = "milk"

  elif re.search(r"(ОАО|ООО|ОДО|УП|УО|РУПП) \"(.*)\"",txt):
    tags["name"] = txt
    tags["office"] = "yes"

  elif re.search(r"(ТЦ|ТД) \"(.*)\"",txt):
    tags["name"] = txt
    tags["shop"] = "mall"

  elif re.search(r"кафе \"(.*)\"",txt):
    tags["name"] = re.search(r"кафе \"(.*)\"",txt).groups()[0]
    tags["amenity"] = "cafe"

  elif re.match(r"магазин \"(.*)\"\w?[(]?(.*)[)]?",txt):
    tt = re.match(r"магазин \"(.*)\"\w?[(]?(.*)[)]?",txt).groups()
    if len(tt) >= 1:
      name = tt[0]
    comment = ""
    if len(tt) >= 2:
      comment = tt[1].strip().strip("(").strip(")")
    tags["name"] = name
    #print name, comment
    if comment in ("круглосуточный", ) or "круглосуточный" in txtl:
      tags["opening_hours"] = "24/7"


    if comment in ("элитные вина","вина", "вино") or "вино" in name:
      tags["shop"] = "wine"
    elif comment in ("морепродукты", ) or "Океан" in name:
      tags["shop"] = "seafood"
    elif comment in ("мебель", ) or "Мебель" in name:
      tags["shop"] = "furniture"
    elif comment in ("хлеб", ) or "хлеб" in txtl:
      tags["shop"] = "bakery"
    elif comment in ("детский", ) or "детский" in txtl:
      tags["shop"] = "toys"
    else:
      tags["shop"] = "convenience"
      

  elif re.search(r"бар \"(.*)\"",txt):
    tags["name"] = re.search(r"бар \"(.*)\"",txt).groups()[0]
    tags["amenity"] = "bar"

  elif re.search(r"(СШ|школа) [ #№N]?([0-9]*)",txt):
    tags["name"] = txt
    tags["ref"] = re.search(r"(СШ|школа) [ #№N]?([0-9]*)",txt).groups()[1]
    tags["amenity"] = "school"

  elif re.search(r"детский сад [ #№N]?([0-9]*)",txt):
    tags["name"] = txt
    tags["ref"] = re.search(r"детский сад [ #№N]?([0-9]*)",txt).groups()[0]
    tags["amenity"] = "kindergarten"

  else: 
    #pass
    tags["description"] = txt


  return tags