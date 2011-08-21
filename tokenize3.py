# -*- coding: utf-8 -*-
import string
import re
import sys

table = [
("quot"," "),("&"," "),
("-я",""),("-й",""),("-ы",""),("-ая",""),("-i",""),
("-"," "),("."," "),
(","," "),("'",""),
("\""," "),
("А","I"),("а","I"),
("Б","B"),("б","B"),
("В","U"),("в","U"),
("Г","H"),("г","H"),
("Д","D"),("д","D"),
("Е","I"),("е","I"),
("Ё","I"),("ё","I"),
("Ж","Z"),("ж","Z"),
("З","Z"),("з","Z"),
("И","I"),("и","I"),
("Й","I"),("й","I"),
("К","K"),("к","K"),
("Л","L"),("л","L"),
("М","M"),("м","M"),
("Н","N"),("н","N"),
("О","I"),("о","I"),
("П","P"),("п","P"),
("Р","P"),("р","P"),
("С","S"),("с","S"),
("Т","T"),("т","T"),
("У","U"),("у","U"),
("Ф","U"),("ф","U"),
("Х","H"),("х","H"),
("Ц","T"),("ц","T"),
("Ч","C"),("ч","C"),
("Ш","S"),("ш","S"),
("Щ","S"),("щ","S"),
("Ъ",""), ("ъ",""),
("Ы","I"),("ы","I"),
("Ь",""), ("ь",""),
("Э","I"),("э","I"),
("Ю","U"),("ю","U"),
("Я","I"),("я","I"),
("Ў","U"),("ў","U"),
("І","I"),("і","I"),
("SC","S"),("II","I"),
("DZ","D"),
("UU","U"),#(" ULICA ",""),
#(" UL "," "),(" PIP "," "),
#(" ZAULAK "," "),
]
def tokenize(text):
  t1 = set(text.split())
  text = " "+ text.upper() +" "
  for s_from, s_to in table:
   text = text.replace(s_from, s_to)
  
  text = text.split()
  t1.update(text)
  text = list(t1)
  text.sort()
  #print text
  return text 




f = open("minsk-relations.osm", "r")
t = {}
streets_j = {}
aaa = 0
relnow = False
tline = ""
nopass = set()
needed=False
for line in f:
  #print line
  if "<rela" in line:
   rgexpr  = re.compile(r'id=\'(.*)\' ti')
   line, = rgexpr.search(line).groups()
   aaa = int(line)
   relnow = True
   needed = False
   tline = ""
  if "</rela" in line:
   relnow = False
   if needed:
    streets_j[aaa] = tline
    a = tokenize(tline)
    streets_j[-aaa] = len(a)
    for b in a:
     if b not in t:
      t[b] =  set((aaa,))
     else:
      t[b].add(aaa)
  if "<member" in line:
    rgexpr  = re.compile(r'type=\'(.*)\' ref=\'(.*)\' role=\'(.*)\'')
    ty, ref, ro =  rgexpr.search(line).groups()
    if ro == "house":
     nopass.add(int(ref))
  if ("<tag" in line) and relnow:
   rgexpr  = re.compile(r'k=\'(.*)\' v=\'(.*)\'')
   k,v = rgexpr.search(line).groups()
   if "name" in k:
     tline = tline + ", " + v
   if "ess:a6" in k:
     needed=True

f.close()
#print t

qw = ["Набережная ул."]

  #print q, tokenize(q)

f = open("out.osm", "r")

rel2way = {}
aaa = 0
waynow = False
tline = ""
needed=False
rgexpr1  = re.compile(r'id=\"(.*)\" ve')
rgexpr2  = re.compile(r'k=\"(.*)\" v=\"(.*)\"')
for line in f:
  #print line
  if "<way" in line:
   
   line, = rgexpr1.search(line).groups()
   aaa = int(line)
   if aaa not in nopass:
    waynow = True
   needed = False
   tline = ""
  if "</way" in line:
   waynow = False
   if needed:
    #print tline ,
    tkns = tokenize (tline)
    sftn = {}
    for tok in tkns:
      if tok in t:
         for z in t[tok]:
          if z in sftn:
            sftn[z] += (1.0 / len(t[tok]))
          else:
            sftn[z] = (1.0 / len(t[tok]))
    mn = 0
    best = 0
    for z in sftn.keys():
     if sftn[z] == mn:
       if (streets_j[-best]) > (streets_j[-z]):
         best = z
         mn = sftn[z]
      #print "===========", tok
      #for z in t[tok]:
     if sftn[z] > mn:
      best = z
      mn = sftn[z]
    
    if best is not 0:
     if best in rel2way:
       rel2way[best].append(aaa)
     else:
       rel2way[best] = [aaa,]
    else:
      sys.stderr.write("%s %s\n"%(aaa,tline))
     #print ",", best, streets_j[best]
     #del streets_j[best]
    #else:
    # print ", 0"  

  if ("<tag" in line) and waynow:
   
   k,v = rgexpr2.search(line).groups()
   if "street" in k:
     tline = tline + " " + v
     needed=True
#print rel2way
f.close()

f = open("minsk-relations.osm", "r")
t = {}
streets_j = {}
aaa = 0
relnow = False
tline = ""
nopass = set()
needed=False
matched = {}
unmatched = set()
for line in f:
  #print line
  if "<rela" in line:
   rgexpr  = re.compile(r'id=\'(.*)\' ti')
   linez, = rgexpr.search(line).groups()
   aaa = int(linez)
   line = line.replace(" id=", " action=\'modify\' id=")
   relnow = True
   
  if "</rela" in line:
   relnow = False
   if aaa in rel2way:
     matched[aaa] = len(rel2way[aaa])
     for zxd in rel2way[aaa]:
       print """    <member type="way" ref="%s" role="house"/>""" % (zxd)
   else:
     unmatched.add(aaa)
  print line,

sys.stderr.write(repr((repr(matched),len(matched), repr(unmatched), len(unmatched))))
f.close()
