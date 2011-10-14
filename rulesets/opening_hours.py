#!/usr/bin/env python
# -*- coding: utf-8 -*-

from rulesets import replace_bunch

def NicifyTags(obj="node", oid=0, tags={}, country = ("",), need_review = False):
  if "opening_hours" in tags:
    oh = tags["opening_hours"].strip()
    oh = replace_bunch(("Пнд", "Пн", "Moд", "Monday", "Mon"), "Mo", oh)
    oh = replace_bunch(("Втр", "Вт", "Tuр", "Tuesday", "Tue"), "Tu", oh)
    oh = replace_bunch(("Срд", "Ср", "Weд", "Wednesday", "Wed"), "We", oh)
    oh = replace_bunch(("Чтв", "Чт", "Thв", "Thursday", "Thu"), "Th", oh)
    oh = replace_bunch(("Птн", "Пят", "Frц", "Frт", "Пт", "Friday", "Fri"), "Fr", oh)
    oh = replace_bunch(("Суб", "Сб", "Saб", "Saturday", "Sat"), "Sa", oh)
    oh = replace_bunch(("Вск", "Вс", "Suк", "Sunday", "Sun"), "Su", oh)


    oh = replace_bunch(("Январь", "Янв"), "Jan", oh)
    oh = replace_bunch(("Февраль", "Фев"), "Feb", oh)
    oh = replace_bunch(("Март", "Мар"), "Mar", oh)
    oh = replace_bunch(("Апрель", "Апр"), "Apr", oh)
    oh = replace_bunch(("Май", ), "May", oh)
    oh = replace_bunch(("Июнь", "Июн"), "Jun", oh)
    oh = replace_bunch(("Июль", "Июл"), "Jul", oh)    
    oh = replace_bunch(("Август", "Авг"), "Aug", oh)    
    oh = replace_bunch(("Сентябрь", "Сен"), "Sep", oh)    
    oh = replace_bunch(("Октябрь", "Окт"), "Oct", oh)    
    oh = replace_bunch(("Ноябрь", "Ноя"), "Nov", oh)    
    oh = replace_bunch(("Декабрь", "Дек"), "Dec", oh)    
    oh = oh.replace("Sa,Su","Sa-Su").strip(";")
    oh = oh.replace(";","; ")
    oh = oh.replace("  "," ")
    tags["opening_hours"] = oh


  return need_review, tags