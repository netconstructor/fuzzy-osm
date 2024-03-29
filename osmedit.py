#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import re
from rulesets import *
from rulesets import Memoize
import rulesets

reload(sys)
sys.setdefaultencoding("utf-8")          # a hack to support UTF-8

ref_pattern = re.compile(u"([a-zA-Zа-яА-Я]*)[ -]*([-0-9]+)$")
fuel_ref = re.compile(u"\s[-#№]*(\d+)\s")
post_ref = re.compile("(?:ПО)?(?:[№N]+[0-9]+[ -]+)?([0-9]{6})$")

ru2en = {u"У":"Y",u"К":"K",u"Е":"E",u"Н":"H",u"Х":"X",u"В":"B",
         u"А":"A",u"Р":"P",u"О":"O",u"С":"C",u"М":"M",u"Т":"T"}
en2ru = {}
for k,v in ru2en.items():
  en2ru[v] = k







unusual_case_punct = dict([(x.decode("utf-8").lower().strip(), x.decode("utf-8").strip()) for x in open("presets/unusual_case_punct","r")])
capital_if_first = dict([(x.decode("utf-8").lower().strip(), x.decode("utf-8").strip()) for x in open("presets/capital_if_first","r")])
#print unusual_case_punct
always_manual = set([x.decode("utf-8").strip() for x in open("presets/always_manual","r")])
property_types = set([x.decode("utf-8").strip() for x in open("presets/property_types","r")])
for t in property_types:
  unusual_case_punct[t.lower()] = t

mistakes = [x.decode("utf-8").strip() for x in open("presets/mistakes","r")]
mistakes = dict([(mistakes[2*i],mistakes[2*i+1]) for i in range(0,len(mistakes)/2) ])
for t in unusual_case_punct:
  if "." in t:
    mistakes[t.replace(".", "")] = unusual_case_punct[t]
#print "".join([k+": "+v+"\n" for k,v in mistakes.iteritems()])


nice_tags_cache = {}



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
    if a in "qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNMā":
      if not fully:
        return True
      latin = True
    elif fully:
      return False
  return latin

@Memoize
def clean_name(need_review, name, what=("street",)):
    oname = name
    name = " " + name.lower() + " "
    name = name.replace(u".", u". ")                                    # Пр.Мира -> Пр. Мира
    if "street" in what:
      #name = name.replace(u",", u" ")                                             # Мира, пр. -> Мира пр.
      name = name.replace(u"Пр.", u" Пр.")                                        # МираПр. -> Мира Пр.
    name = name.replace(u"№", u" №")
    name = name.replace(u"№ ", u"№")
    name = name.replace(u"№;", u"№")
    #name = name.replace(u"/", u" / ")
    name = name.replace(u"(", u" ( ")
    name = name.replace(u")", u" ) ")
    name = name.replace(u",", u" , ")
    name = name.replace(u";", u" ; ")
    name = name.replace(u" -", u" - ")
    name = name.replace(u"- ", u" - ")
    name = name.replace(u"–", u" - ")
    name = name.replace(u"*", u" * ")
    
    
    for tr in mistakes:
      name = name.replace(" "+tr+" ", " "+mistakes[tr]+" ")

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
          if ba in property_types:
            First = True

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
                      
                    if First and ta in capital_if_first:
                      ta = capital_if_first[ta]
                      ta = ta[0].upper() + ta[1:]
                    elif not First and ta in capital_if_first:
                      ta = capital_if_first[ta]
                    elif ta in unusual_case_punct:                                        # необычный регистр, типа ул. или МОПРа
                      ta = unusual_case_punct[ta]
                    elif ("street" in what) or First or isLatin(ta):                 # для улиц первые прописные, для остальных пои - прописные после кавычек и английские слова
                      ta = ta[0].upper() + ta[1:]                                       # иначе поднимаем первую букву
                    First = False
                    if ta in property_types:
                      First = True


                  tt.append(ta)
                ta = '"'.join(tt)
              tq.append(ta)
          tz = "-".join(tq)
          t.append(tz)
      name = " ".join(t)
      name = name.replace(u"( -)", u" ")
      name = name.replace(u"( )", u" ")
      name = name.replace(u" )", u")")
      name = name.replace(u"( ", u"(")
      name = name.replace(u" ;", u";")
      name = name.replace(u" ,", u",")
      name = name.replace(u"A / S", u"A/S")
      if name and name[0] == '"' and name[-1] == '"':
        name = name.strip('"')
      #if name != oname:
      #print name
    return need_review, name



def FormattedTagsPrint(tags):
  ll = tags.keys()
  ll.sort()
  for k in ll:
    print "%15s = %30s"%(k, tags[k])


def NicifyTags(obj="node", oid=0, tags={}, country = ("BY",)):
  """
  Generates a better variants for some tags.
  Gives back a dictionary of possible values.
  """
  need_review = False                                                           # отметка о том, что набор ключей требует вмешательства человека
  if repr(tags)+repr(obj) in nice_tags_cache:
    return nice_tags_cache[repr(tags)+repr(obj)]
  changes = {}
  
  otags = tags.copy()
  tags = tags.copy()
  need_review, tags = rulesets.yesno.NicifyTags           (obj, oid, tags, country, need_review)
  if 'opening_hours' in tags:
    need_review, tags = rulesets.opening_hours.NicifyTags (obj, oid, tags, country, need_review)
  need_review, tags = rulesets.bridges.NicifyTags         (obj, oid, tags, country, need_review)
  need_review, tags = rulesets.entrances.NicifyTags       (obj, oid, tags, country, need_review)
  need_review, tags = rulesets.capt_o.NicifyTags          (obj, oid, tags, country, need_review)
  need_review, tags = rulesets.water.NicifyTags           (obj, oid, tags, country, need_review)
  need_review, tags = rulesets.cladr.NicifyTags           (obj, oid, tags, country, need_review)
  need_review, tags = rulesets.garbage_tags.NicifyTags    (obj, oid, tags, country, need_review)


  refs = set()                                                                  # множество вариантов написания ref'а
  if "highway" in tags:
    if "name" in tags:
      if tags["name"] == "S/N":
        del tags["name"]
        tags["highway"] = "service"
    for ref_key in ("ref", "nat_ref", "int_ref"):
      if ref_key in tags and country[0] in ("RU", "BY", "UA", "LV"):
        refs.add(tags[ref_key])
        tags[ref_key] = tags[ref_key].replace(",",";")
        a = ref_pattern.match(tags[ref_key])
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
          elif tlr in tags.get("name","").lower():
            del tags[ref_key]
          elif tlr in ("paved","unpaved"):
            tags["surface"] = tlr
            del tags[ref_key]
          elif tlr in ("bing","yahoo"):
            tags["source"] = tlr
            del tags[ref_key]
          elif "iela" in tlr or "szlak" in tlr or "проспект" in tlr or "улица" in tlr or "переулок" in tlr or "тропа" in tlr:
            if "name" not in tags:
              refs.discard(tags[ref_key])
              del tags[ref_key]
              tags["name"] = tlr
              need_review, tags["name"] = clean_name(need_review, tags["name"], ("street",))
            else:
              need_review = True
            
          else:
            need_review = True
    if "level" in tags:
      tags["layer"] = tags["level"]
      del tags["level"]

  for ref_key in ("ref", "nat_ref", "int_ref"):                                 # собираем возможные ref
    if ref_key in tags:
      refs.add(tags[ref_key])
  if u"name" in tags:                                                           # если name == ref, то нафиг такой name
    if tags["name"] in refs:
      del tags["name"]
  

  if "name" in tags:
    if ";" in tags["name"]:
      tn = tags["name"].split(";")
      tn = list(set([t.strip() for t in tn]))
      tn.sort()
      tags["name"] = "; ".join(tn).strip()
    
  if "waterway" in tags:
    if "name" in tags:
      tags["name"] = " "+tags["name"].lower()+" "
      tags["name"] = tags["name"].replace(" p. ","")
      tags["name"] = tags["name"].replace(" р. ","")
      tags["name"] = tags["name"].replace(" pека ","")
      need_review, tags["name"] = clean_name(need_review, tags["name"], ("street",))
  if ("highway" in tags or "waterway" in tags) and obj != "node":
    if "name" in tags and not ("RU" in country and "highway" in tags):  # в россии тегом name занимается AMDmi3
      need_review, tags["name"] = clean_name(need_review, tags["name"], ("street",))
      
    if "name:ru" in tags:
      need_review, tags["name:ru"] = clean_name(need_review, tags["name:ru"], ("street",))
    if tags.get("name","").lower() in ("sidewalk", "тротуар"):
      del tags["name"]
      tags["highway"] = "footway"
      tags["footway"] = "sidewalk"

  
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
          name = name.replace(t, "").strip()
      for t in (u"платная","paid"):
        if t in name:
          tags[u"fee"] = u"yes"
          name = name.replace(t, "").strip()
      if name in ("гаражи",):
        tags["landuse"] = "garages"
        if tags.get("amenity","") == "parking":
          del tags["amenity"]
      need_review, tags["name"] = clean_name(need_review, tags["name"], ("POI",))
      if name in ("парковка", "стоянка", "автостоянка", "гаражи", "автомобильная стоянка"):
        if tags.get("name:ru","").lower() == tags.get("name","").lower():
          del tags["name:ru"]
        del tags["name"]
      



  if tags.get("amenity","") == "post_office":
    if tags.get("type","") == "oil":
      del tags["type"]
    if tags.get("name","").lower() in ("почта","pasts"):
      del tags["name"]
    if tags.get("ref","").lower() in ("почта","pasts"):
      del tags["ref"]
    if tags.get("addr:postcode","").lower() in ("почта","pasts"):
      del tags["addr:postcode"]
    if post_ref.search(tags.get("name","")):
      tags["ref"] = post_ref.search(tags.get("name","")).groups()[0]
      if tags.get("name:ru","") == tags.get("name",""):
        del tags["name:ru"]
      del tags["name"]
    if post_ref.search(tags.get("ref","")):
      tags["ref"] = post_ref.search(tags.get("ref","")).groups()[0]

    if "ref" in tags and "addr:postcode" not in tags:
      tags["addr:postcode"] = tags["ref"]
    if "ref" not in tags and "addr:postcode" in tags:
      tags["ref"] = tags["addr:postcode"]




  if "building" in tags:
    if "landuse" in tags:
      if tags["building"] in ("yes", "house", "*", tags["landuse"]):
        tags["building"] = tags["landuse"]
        del tags["landuse"]
      elif (tags["building"] in ("dormitory", "apartments") and tags["landuse"] == "residential"):
        del tags["landuse"]
      elif (tags["building"] in ("factory","office") and tags["landuse"] == "industrial"):
        del tags["landuse"]
      elif (tags["building"] in ("warehouse","store") and tags["landuse"] in ("commercial","retail")):
        del tags["landuse"]
      elif (tags["building"] in ("garage","garages") and tags["landuse"] == "garages"):
        del tags["landuse"]
      elif (tags["building"] in ("hangar",) and tags["landuse"] == "garages"):
        tags["building"] = tags["landuse"]
        del tags["landuse"]
      else:
        need_review = True

    if "addr:housenumber" in tags:
      if "addr:housename" in tags:
        if tags["addr:housenumber"] == tags["addr:housename"]:
          del tags["addr:housename"]
      if "name" in tags:
        if tags["name"] == tags["addr:housenumber"]:
          if tags["addr:housenumber"][0].isdigit():
            del tags["name"]
          else:
            need_review = True





  if (tags.get("landuse","") in ("industrial", "residential") and "BY" in country) or tags.get("boundary","") in ("national_park",):
    if "name" in tags:
      need_review, tags["name"] = clean_name(need_review, tags["name"], ("POI",))
    if "name:ru" in tags:
      need_review, tags["name:ru"] = clean_name(need_review, tags["name:ru"], ("POI",))
    if tags.get("name","").lower().strip() in ("гаражи", ):
      del tags["name"]
      tags["landuse"] = "garages"

  if "postal_code" in tags:
    tags["addr:postcode"] = tags["postal_code"]
    del tags["postal_code"]
  
  if "place_name" in tags:
    if tags["place_name"] in ("hamlet", "village"):
      tags["place"] = tags["place_name"]
      del tags["place_name"]
    elif not "name" in tags or tags["place_name"].lower() == tags.get("name","").lower():
      tags["name"] = tags["place_name"]
      del tags["place_name"]
    else:
      need_review = True

  if "place_name:ru" in tags:
    if not "name:ru" in tags or tags["place_name:ru"].lower() == tags.get("name:ru","").lower():
      tags["name:ru"] = tags["place_name:ru"]
      del tags["place_name:ru"]

  if "place_name:en" in tags:
    if not "name:en" in tags or tags["place_name:en"].lower() == tags.get("name:en","").lower():
      tags["name:en"] = tags["place_name:en"]
      del tags["place_name:en"]

  if tags.get("boundary") == "administrative" and "place" in tags and "admin_level" not in tags:
    del tags["boundary"]




  if tags.get("amenity", "") == "fuel":
    if "name" in tags:
      name = tags["name"]
      name = " "+name.lower()+" "
      name = name.replace(u" мазс ", u" ")
      name = name.replace(u" заправка ", u" ")
      name = name.replace(u"азс", u" ")
      name = name.replace(u"'", u" ")
      name = name.replace(u"station", u" ")
      name = name.replace(u"petrol", u" ")
      name = name.replace(u"ln", u" latvijas nafta ")
      #name = name.replace(u"\"", u" ")
      for t in (u"природный газ", u"метаном", u"метан", u"сжатый", u"cng"): #, u"агнкс"): - убрано по просьбе mixdm
        if t in name:
          tags[u"fuel:cng"]=u"yes"
          name = name.replace(t, u" ")
      for t in (u"агзс", "газс", "азгс", u"gaz", u"газовая заправка", u"сжиженный", u"lpg",
      u" газовая заправка", u"gas", u" газ ", u"газ-пропан", "агнс", "газовая", "пропан"):
        if t in name:
          tags[u"fuel:lpg"]=u"yes"
          name = name.replace(t, u" ")
      if tags.get("name:en",'').lower() == 'lpg':
        del tags['name:en']
        tags[u"fuel:lpg"] = u"yes"
        
      need_review, name = clean_name(need_review,name, ("POI",))
      name = " "+name.lower()+" "
      name = name.replace(u" - ", u" ")
      ref = fuel_ref.search(name)
      if ref:
        r = ref.groups()[0]
        if r not in ("123","777"):
          name = fuel_ref.sub(u"",name)
          tags["ref"] = r
      need_review, name = clean_name(need_review,name, ("POI",))

      if name:
        if "name" in tags and tags.get("operator","") == tags["name"]:
          del tags["name"]
        else:
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
  if "is_in" in tags:
    if tags["is_in"].lower() in (tags.get("addr:country","").lower(), tags.get("addr:district","").lower(),tags.get("addr:city","").lower()):
      del tags["is_in"]
  if "is_in:country" in tags:
    if tags["is_in:country"] == "Georgia":
      tags["addr:country"] = "GE"
      del tags["is_in:country"]
  if "is_in:district" in tags:
    tags["addr:district"] = tags["is_in:district"]
    del tags["is_in:district"]
  if "is_in:region" in tags:
    tags["addr:region"] = tags["is_in:region"]
    del tags["is_in:region"]
  if "is_in" in tags and "building" in tags:
    if tags["is_in"].lower() in ("russia", "ru", "россия"):
      del tags["is_in"]
      tags["addr:country"] = "RU"
    else:
      need_review = True


  if "BY" in country:
    tags = NicifyTagsBY(obj,oid,tags)
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
    
  if not equal:
    pass
  
  if need_review:
    print ""
    print "http://openstreetmap.org/browse/%s/%s"%(obj,oid)
    FormattedTagsPrint(tags)
    #print ""

    #FormattedTagsPrint(otags)
    #print ""
  nice_tags_cache[repr(otags)+repr(obj)] = tags
  return tags

def NicifyTagsBY(obj="node", oid=0, tags={}):
  if obj == 'way' and tags.get('addr:country', 'BY') == 'BY':
    if "ref" in tags:                                                           # добиваем ref на основе nat_ref
      if tags["ref"][0] in "MPH":
        if "nat_ref" not in tags:
          tags["nat_ref"] = cyr_ref(tags["ref"])
    if "nat_ref" in tags:                                                       # ...и nat_ref на основе ref
      if "ref" not in tags:
        tags["ref"] = lat_ref(tags["nat_ref"])
    if "highway" in tags:
      if "name" not in tags:
        if tags["highway"] == "living_street":
          tags["highway"] = "service"
          tags["living_street"] = "yes"



    if "service" in tags:
      if "living_street" in tags and tags["service"] == "parikng_aisle":
        del tags["service"]

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
          if 'junction' not in tags and float(tags.get("lanes",0))<4:
            
            if tags['highway'] not in ('unclassified', 'track', 'path', 'footway', 'residential', 'road', 'service', 'pedestrian', 'construction', 'cycleway', 'steps', 'bridlway', 'services', 'motorway_link', 'trunk_link', 'primary_link','secondary_link', 'tertiary_link', 'proposed'):
              tags['highway'] = 'unclassified'
  ### TODO: Better ukrainian processing
  if  u"name" in tags:
    name = tags["name"]                                                         # если встретится явный белорусский в name
    for bel_char  in (u"і",u"ў", u"вул."):
      if bel_char in name.lower():
        is_uk = False
        if tags.get("name:uk") == tags["name"]:
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
  if "highway" in tags and "name" in tags:
    tags["name"] = tags["name"].replace("G.","g.")

  return tags
  