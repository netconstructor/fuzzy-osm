#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import re

reload(sys)
sys.setdefaultencoding("utf-8")          # a hack to support UTF-8

ref_pattern = re.compile(u"([a-zA-Zа-яА-Я]*)[ -]*([-0-9]+)")
fuel_ref = re.compile(u"\s[-#№](\d+)")
post_ref = re.compile("(?:[№N]+[0-9]+[ -]+)?([0-9]{6})")

ru2en = {u"У":"Y",u"К":"K",u"Е":"E",u"Н":"H",u"Х":"X",u"В":"B",
         u"А":"A",u"Р":"P",u"О":"O",u"С":"C",u"М":"M",u"Т":"T"}
en2ru = {}
for k,v in ru2en.items():
  en2ru[v] = k

garbage_values = frozenset([".", "-", ",", "", "(", "-)", "()", "FIXME"])

unusual_case_punct = dict([(x.decode("utf-8").lower().strip(), x.decode("utf-8").strip()) for x in open("presets/unusual_case_punct","r")])
#print unusual_case_punct
always_manual = set([x.decode("utf-8").strip() for x in open("presets/always_manual","r")])

mistakes = [x.decode("utf-8").strip() for x in open("presets/mistakes","r")]
mistakes = dict([(mistakes[2*i],mistakes[2*i+1]) for i in range(0,len(mistakes)/2) ])
for t in unusual_case_punct:
  if "." in t:
    mistakes[t.replace(".", "")] = unusual_case_punct[t]
#print "".join([k+": "+v+"\n" for k,v in mistakes.iteritems()])


nice_tags_cache = {}

def replace_bunch(bunch, to, where):
  for z in bunch:
    where = where.replace(z, to)
  return where

def cyr_ref(ref):
  for i in en2ru:
    ref = ref.replace (i,en2ru[i])
  return ref

def lat_ref(ref):
  for i in ru2en:
    ref = ref.replace (i,ru2en[i])
  return ref

def isLatin(string, fully = False):
  latin = False
  for a in string:
    if a in "qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM":
      if not fully:
        return True
      latin = True
    elif fully:
      return False
  return latin

def clean_name(need_review, name, what=("street",)):
    oname = name
    if name in garbage_values:
      return u""
    name = name.replace(u".", u". ")                                    # Пр.Мира -> Пр. Мира
    if "street" in what:
      name = name.replace(u",", u" ")                                             # Мира, пр. -> Мира пр.
      name = name.replace(u"Пр.", u" Пр.")                                        # МираПр. -> Мира Пр.
    name = name.replace(u"№", u" №")
    name = name.replace(u"№ ", u"№")
    name = name.replace(u"/", u" / ")
    name = " " + name.lower() + " "
    for tr in mistakes:
      name = name.replace(" "+tr+" ", " "+mistakes[tr]+" ")
    if "street" in what:
      if " набережная" in name:                                                   # _Н_абережная ул., но Комсомольская _н_абережная
        if ("ул" in name) or (len(name.strip()) == len(u"набережная")):
          name = name.replace("набережная", "Набережная")
    for i in (u"\"",u"«",u"»",u"`"):
      name = name.replace(i, u'"')

    if name in unusual_case_punct:                                        # необычный регистр, типа ул. или МОПРа
      name = unusual_case_punct[name]
    else:
      name = name.split()                                                         # кромсаем по словам
      t = []
      First = True
      for ba in name:
        if ba in mistakes:                                                        # опечатки, типа Тимерязева -> Тимирязева
          ba = mistakes[ba]
        if ba in always_manual:                                                   # если там что-то типа "возможная кольцевая" - жаловаться
          need_review = True
        if ba in unusual_case_punct:                                        # необычный регистр, типа ул. или МОПРа
          ba = unusual_case_punct[ba]
          t.append(ba)
          First = False
        else:
          tq = []                                                                   # кромсаем по дефисам
          tz = ba.split("-")                                                        # если [цифры]-[буквы], то это 1-я или 15-го, регистр не поднимать
          if len(tz) == 2 and tz[0].isdigit():
            tq = tz

          else:
            for ta in tz:
              if ta:
                tp = ta.split('"')
                if tp[0] == "":
                  First = True
                tt = []
                for ta in tp:
                  if ta:
                    if ta in always_manual:                                             # жаловаемся на хрень
                      need_review = True
                    if ta in mistakes:                                                  # правим очепятки
                      ta = mistakes[ta]
                    if ta in unusual_case_punct:                                        # необычный регистр, типа ул. или МОПРа
                      ta = unusual_case_punct[ta]
                    elif ("street" in what) or First or isLatin(ta):                 # для улиц первые прописные, для остальных пои - прописные после кавычек и английские слова
                      ta = ta[0].upper() + ta[1:]                                       # иначе поднимаем первую букву
                    First = False
                  tt.append(ta)
                ta = '"'.join(tt)
              tq.append(ta)
          tz = "-".join(tq)
          t.append(tz)
      name = " ".join(t)
      name = name.replace(u"( -)", u" ")
      name = name.replace(u"( )", u" ")
      name = name.replace(u" )", u")")
      #if name != oname:
      #print name
    return need_review, name



def OsmTagsEditor(tags, newtags = []):
  """
  Gets tags and suggestions, gives back a set of tags and "modified" flag
  """
  pass

def FormattedTagsPrint(tags):
  ll = tags.keys()
  ll.sort()
  for k in ll:
    print "%15s = %30s"%(k, tags[k])


def NicifyTags(obj="node", oid=0, tags={}):
  """
  Generates a better variants for some tags.
  Gives back a dictionary of possible values.
  """
  need_review = False                                                           # отметка о том, что набор ключей требует вмешательства человека
  taghash = obj+repr(tags)                                                      # кеш - человека не надо спрашивать по два раза
  if taghash in nice_tags_cache:
    return nice_tags_cache[taghash]
  changes = {}
  otags = tags.copy()
  tags = tags.copy()


  for key in tags.keys():
    tags[key] = tags[key].strip()
    if tags[key] in garbage_values:
      del tags[key]
  refs = set()                                                                  # множество вариантов написания ref'а
  if "highway" in tags:
    for ref_key in ("ref", "nat_ref", "int_ref"):
      if ref_key in tags:
        refs.add(tags[ref_key])
        a = ref_pattern.search(tags[ref_key])
        if a:
          letter, num = a.groups()
          letter = letter.upper()
          letter = lat_ref(letter)
          if letter == "E":                                                     # E-маршруты пишутся через пробел
            letter = "E "
          if letter == "T":                                                     # Украина, территориальные дороги
            letter = "Т-"
          if letter == "O":
            letter = "О-"
          if "nat" in ref_key:
            tags[ref_key] = cyr_ref((letter + str(num)).strip())
          else:
            tags[ref_key] = lat_ref((letter + str(num)).strip())
        else:
          tlr = tags[ref_key].lower()
          if "на " in tlr or "to " in tlr or "то " in tlr:                      # убиваем ref="на Берлин"
            if tags.get("name","").lower() == tlr:
              del tags["name"]                                                  # убиваем name="на Берлин" заодно
            del tags[ref_key]
          elif tags.get("name","").lower() == tlr:                              # убиваем ref=Челюскинцев при name=Челюскинцев
            del tags[ref_key]
          else:
            need_review = True
    if "ref" in tags:                                                           # добиваем ref на основе nat_ref
      if tags["ref"][0] in "MPH":
        if "nat_ref" not in tags:
          tags["nat_ref"] = cyr_ref(tags["ref"])
    if "nat_ref" in tags:                                                       # ...и nat_ref на основе ref
      if "ref" not in tags:
        tags["ref"] = lat_ref(tags["nat_ref"])
  for ref_key in ("ref", "nat_ref", "int_ref"):                                 # собираем возможные ref
    if ref_key in tags:
      refs.add(tags[ref_key])
  if u"name" in tags:                                                           # если name == ref, то нафиг такой name
    if tags["name"] in refs:
      del tags["name"]
      
  ### TODO: Better ukrainian processing
  if False and u"name" in tags:
    name = tags["name"]                                                         # если встретится явный белорусский в name
    for bel_char  in (u"і",u"ў", u"вул."):
      if bel_char in name.lower():
        is_uk = False
        if tags["name:uk"] == tags["name"]:
          is_uk = True
        for uk_char in (u"и",u"ї",u"ґ",u"є"):
          if uk_char in name.lower():
            tags["name:uk"] = tags["name"]
            is_uk = True
            break
        if is_uk:
          break
        if "name:be" not in tags:                                               # унести его в name:be
          tags["name:be"] = tags["name"]
        if tags["name:be"] == name:
          if "name:ru" in tags:
            tags["name"] = tags["name:ru"]                                      # вернуть на место name:ru
          else:
            del tags["name"]                                                    # или хотя бы пожаловаться
            need_review = True
            tags["fixme:komzpa"] = u"добавить русское имя"
            break
  if ("highway" in tags or "waterway" in tags) and obj != "node":
    if "name" in tags:
      need_review, tags["name"] = clean_name(need_review, tags["name"], ("street",))
      
    if "name:ru" in tags:
      need_review, tags["name:ru"] = clean_name(need_review, tags["name:ru"], ("street",))
  if "created_by" in tags:
    del tags["created_by"]
  if "waterway" in tags and "natural" in tags:
    if tags["waterway"] == "riverbank" and "name" in tags and tags["natural"]=="water":
      del tags["natural"]
      del tags["name"]
      need_review = True
  
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


  if tags.get("amenity","") == "parking" or tags.get("landuse","") == "garages":
    if "name" in tags:
      name = tags["name"].lower()
      for t in (u",бесплатная","free"):
        if t in name:
          tags[u"fee"]=u"no"
          name = name.replace(t, u"").strip()      
      for t in (u"платная","paid"):
        if t in name:
          tags[u"fee"]=u"yes"
          name = name.replace(t, u"").strip()
      if name in ("гаражи",):
        tags["landuse"] = "garages"
        if tags.get("amenity","") == "parking":
          del tags["amenity"]
      if name in ("парковка", "стоянка", "автостоянка", "гаражи"):
        if tags.get("name:ru","").lower() == tags.get("name","").lower():
          del tags["name:ru"]
        del tags["name"]

  if tags.get("amenity","") == "school":
    if "name" in tags:
      name = tags["name"].lower()
      if name in ("школа",):
        del tags["name"]

  if tags.get("amenity","") == "post_office":
    if tags.get("type","") == "oil":
      del tags["type"]
    if tags.get("name","") == "Почта":
      del tags["name"]
    if post_ref.search(tags.get("name","")):
      tags["ref"] = post_ref.search(tags.get("name","")).groups()[0]
      if tags.get("name:ru","") == tags.get("name",""):
        del tags["name:ru"]
      del tags["name"]
    if "ref" in tags and "addr:postcode" not in tags:
      tags["addr:postcode"] = tags["ref"]
    if "ref" not in tags and "addr:postcode" in tags:
      tags["ref"] = tags["addr:postcode"]


  if "building" in tags:
    if "addr:housenumber" in tags:
      if "addr:housename" in tags:
        if tags["addr:housenumber"] == tags["addr:housename"]:
          del tags["addr:housename"]
      if "name" in tags:
        if tags["name"] == tags["addr:housenumber"]:
          if tags["addr:housenumber"].isdigit():
            del tags["name"]
          else:
            del tags["addr:housenumber"]


  if tags.get("amenity","") == "cafe":
    if tags.get("name","").lower().strip() in ("кафе",):
      del tags["name"]
    if tags.get("name:ru","").lower().strip() in ("кафе",):
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


  if tags.get("landuse","") in ("industrial", "residential"):
    if "name" in tags:
      need_review, tags["name"] = clean_name(need_review, tags["name"], ("POI",))
    if "name:ru" in tags:
      need_review, tags["name:ru"] = clean_name(need_review, tags["name:ru"], ("POI",))
    if tags.get("name","").lower().strip() in ("гаражи", ):
      del tags["name"]
      tags["landuse"] = "garages"




  if obj == 'way':
    if "highway" in tags:
      if  "name" not in tags and tags["highway"] == "living_street":
        tags["highway"] = "service"
        tags["living_street"] = "yes"

    if "service" in tags:
      if "living_street" in tags and tags["service"] == "parikng_aisle":
        del tags["service"]
  if tags.get("addr:country","").lower() in ("by", "ru"):
    del tags["addr:country"]
  if "addr:city" in tags:
    del tags["addr:city"]
  if "addr:region" in tags:
    del tags["addr:region"]
  if "postal_code" in tags:
    tags["addr:postcode"] = tags["postal_code"]
    del tags["postal_code"]
  if "cladr:name" in tags:
    if tags["cladr:name"].lower() == tags.get("name","").lower():
      del tags["cladr:name"]

  
  if obj == 'way':
    if 'highway' in tags:
      if 'ref' in tags:
        rclass = tags['ref'][0]
        if rclass == 'M':
          if tags['highway'] not in ('motorway','motorway_link','trunk','trunk_link'):
            tags['highway'] = 'trunk'
        if rclass == 'P':
          if tags['highway'] not in ('primary','primary_link','secondary','secondary_link'):
            tags['highway'] = 'primary'
        if rclass == 'H':
          if tags['highway'] not in ('secondary','secondary_link','tertiary','tertiary_link'):
            tags['highway'] = 'tertiary'
      if False: # else: ## временно отключено, ждём армагеддец
        if 'name' not in tags:
          if 'junction' not in tags:
            if tags['highway'] not in ('unclassified', 'track', 'path', 'footway', 'residential', 'road', 'service', 'pedestrian', 'construction', 'cycleway', 'steps', 'bridlway', 'services', 'motorway_link', 'trunk_link', 'primary_link','secondary_link', 'tertiary_link', 'proposed'):
              tags['highway'] = 'unclassified'
  if tags.get("amenity", "") == "fuel":
    if "name" in tags:
      name = tags["name"]
      name = " "+name.lower()+" "
      name = name.replace(u"азс", u" ")
      name = name.replace(u"'", u" ")
      name = name.replace(u"station", u" ")
      name = name.replace(u"\"", u" ")
      for t in (u"природный газ", u"метан", u"сжатый", u"cng"): #, u"агнкс"): - убрано по просьбе mixdm
        if t in name:
          tags[u"fuel:cng"]=u"yes"
          name = name.replace(t, u" ")
      for t in (u"агзс", u"gaz", u"газовая заправка", u"сжиженный", u"lpg",
      u" газовая заправка", u"gas", u" газ ", u"газ-пропан"):
        if t in name:
          tags[u"fuel:lpg"]=u"yes"
          name = name.replace(t, u" ")
      need_review, name = clean_name(need_review,name, ("POI",))
      name = " "+name.lower()+" "
      name = name.replace(u" - ", u"")
      ref = fuel_ref.search(name)
      if ref:
        r = ref.groups()[0]
        name = fuel_ref.sub(u"",name)
        tags["ref"] = r
      need_review, name = clean_name(need_review,name, ("POI",))
      if name:
        if tags.get("name:ru","") == tags["name"]:
          tags["name:ru"] = name
        tags["name"] = name
      else:
        if tags.get("name:ru","") == tags["name"]:
          del tags["name:ru"]
        del tags["name"]
  if "url" in tags:
    if "website" in tags:
      if tags["website"] == tags["url"]:
        del tags["url"]
      else:
        need_review = True
    else:
      tags["website"] = tags["url"]
      del tags["url"]
  if "opening_hours" in tags:
    oh = tags["opening_hours"]
    oh = replace_bunch(("Пн", "Monday", "Mon"), "Mo", oh)
    oh = replace_bunch(("Вт", "Tuesday", "Tue"), "Tu", oh)
    oh = replace_bunch(("Ср", "Wednesday", "Wed"), "We", oh)
    oh = replace_bunch(("Чт", "Thursday", "Thu"), "Th", oh)
    oh = replace_bunch(("Пт", "Friday", "Fri"), "Fr", oh)
    oh = replace_bunch(("Сб", "Saturday", "Sat"), "Sa", oh)
    oh = replace_bunch(("Вс", "Sunday", "Sun"), "Su", oh)
    oh = oh.replace("Sa,Su","Sa-Su")
    oh = oh.replace(";","; ")
    oh = oh.replace("  "," ")
    tags["opening_hours"] = oh
    del oh
  equal = True
  if len(tags) == len(otags):
    for k in tags:
      if k in otags:
        equal = otags[k] == tags[k]
        if not equal:
          break
      else:
        equal = False
        break
  else:
    equal = False
  nice_tags_cache[taghash] = tags
  if need_review:
    print ""
    print "http://openstreetmap.org/browse/%s/%s"%(obj,oid)
    FormattedTagsPrint(tags)
    #print ""

    #FormattedTagsPrint(otags)
    #print ""

  return tags
