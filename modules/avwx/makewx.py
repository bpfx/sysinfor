#!/bin/env python

# https://aviationweather.gov/adds/dataserver_current/httpparam?dataSource=metars&requestType=retrieve&format=xml&stationString=KDEN%20KSEA%20PHNL&hoursBeforeNow=2
# dataSource=metars
# requestType=retrieve
# format=xml
# stationString=KDEN%20KSEA%20PHNL
# hoursBeforeNow=1

import requests
import json
from mako.template import Template
from datetime import datetime
from dateutil import tz
from avwx.models import MetarSet

from_zone = tz.gettz('Zulu')
to_zone = tz.gettz('America/Chicago')

URL="https://aviationweather.gov/adds/dataserver_current/httpparam"
saveDir = "/Users/bob/work/sysinfor/modules/avwx/html"
templateFile = "avwx.template"
htmlTemplate = saveDir + "/" + templateFile
dSource = "metars"
rType = "retrieve"

# Walk through list and get json

def make_query(airport):
  metar = MetarSet(airport)
  metar.refresh()
  latest_metar = metar.get_latest()
  return latest_metar

def setupWind(inputData):
  if inputData['Wind-Gust'] > 0:
    gust = " G" + inputData['Wind-Gust']
  return inputData['Wind-Direction'] + " @ " + inputData['Wind-Speed'] + "kts"+ gust

def convertTemp(temp):
  return (int(temp)*1.8)+32

def convertTime(datet):
  print datet
  day = datet[:2]
  timez = datet[2:6]
  utc = datetime.strptime(timez, '%H%M')
  utc = utc.replace(tzinfo=from_zone)
  central = utc.astimezone(to_zone)
  print central.time()
  return central + " Central, Day:" + day

def buildHtml(inputData):
  print inputData.detail_string()
  mytemplate = Template(filename=htmlTemplate)
  location=inputData.station
  #curtime=convertTime(inputData.observation_time)
  curtime="Hello"
  conditions=inputData.flight_category
  wind=inputData
  temperature=convertTemp(inputData.temp)
  dewpoint=convertTemp(inputData.dewpoint)
  altimeter=inputData.altimeter
  print mytemplate.render(
    airport=location,
    time=curtime,
    conditions=conditions,
    wind=wind,
    temperature=temperature,
    dewpoint=dewpoint,
    altimeter=altimeter)

airportList = ['KDTO']

for x in airportList:
  completedRequest = make_query(x)
  buildHtml(completedRequest)
