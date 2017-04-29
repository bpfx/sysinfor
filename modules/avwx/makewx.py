#!/bin/env python

# 0 raw_text,
# 1 station_id,
# 2 observation_time,
# 3 latitude,
# 4 longitude,
# 5 temp_c,
# 6 dewpoint_c,
# 7 wind_dir_degrees,
# 8 wind_speed_kt,
# 9 wind_gust_kt,
# 10 visibility_statute_mi,
# 11 altim_in_hg,
# 12 sea_level_pressure_mb,
# 13 corrected,
# 14 auto,
# 15 auto_station,
# 16 maintenance_indicator_on,
# 17 no_signal,
# 18 lightning_sensor_off,
# 19 freezing_rain_sensor_off,
# 20 present_weather_sensor_off,
# 21 wx_string,
# 22 sky_cover,
# 23 cloud_base_ft_agl,
# 24 sky_cover,
# 25 cloud_base_ft_agl,
# 26 sky_cover,
# 27 cloud_base_ft_agl,
# 28 sky_cover,
# 29 cloud_base_ft_agl,
# 30 flight_category,
# 31 three_hr_pressure_tendency_mb,
# 32 maxT_c,
# 33 minT_c,
# 34 maxT24hr_c,
# 35 minT24hr_c,
# 36 precip_in,
# 37 pcp3hr_in,
# 38 pcp6hr_in,
# 39 pcp24hr_in,
# 40 snow_in,
# 41 vert_vis_ft,
# 42 metar_type,
# 43 elevation_m

import requests
import json
from mako.template import Template
from datetime import datetime
from dateutil import tz
import csv
import os

from_zone = tz.gettz('Zulu')
to_zone = tz.gettz('America/Chicago')

# Setup where everything is
# mainDir: Where the module lives
#   todo: when sysinfor is further along, might make this one of those cool
#         auto-finding-where-everything-is-dynamically-in-a-pythony-way-things
mainDir = "/Users/bob/work/sysinfor/modules/avwx"

# wxDir: where the wx csv lives
wxDir = mainDir + "/wx"
wxFile = wxDir + "/" + "metars.cache.csv"

# htmlDir: Where to save the htmls
htmlDir = mainDir + "/html"
templateFile = "avwx.template"
htmlTemplate = htmlDir + "/" + templateFile

# sysinforSaveDir = where to save the outpus so sysinfor can find it
sysinforSaveDir = htmlDir + "/sysinfor"

# WRite out what this function does
def getWxFromFile():
  with open(wxFile, 'rb') as csvFile:
    reader = csv.reader(csvFile)
    wxList = list(reader)
    return wxList

def getAirportWx(theList,airport):
  for line in theList:
    if line[1] == airport:
      return line
  return Null

def convertTemp(temp):
  return (float(temp)*1.8)+32

def convertTime(datet):
  # 2017-04-29T15:27:00Z
  utc = datetime.strptime(datet, '%Y-%m-%dT%H:%M:%SZ')
  utc = utc.replace(tzinfo=from_zone)
  central = utc.astimezone(to_zone)
  cTime = central.time()
  cDate = central.date()
  cFull = str(cTime) + " " + str(cDate)
  uTime = utc.time()
  uDate = utc.date()
  uFull = str(uTime) + " " + str(uDate)
  rdateT = {'local': cFull, 'zulu': uFull}
  return rdateT

def makeWind(direction, speed, gust):
  if gust is not None:
    theWind = direction + " @ " + speed + "G" + gust
  else:
      theWind = direction + " @ " + speed
  return theWind

def buildClouds(rawClouds):
  prettyClouds = {}
  layerList = ['layer1','layer2','layer3','layer4']
  for entry in layerList:
    if rawClouds[entry][0] != "":
      prettyClouds[entry] = rawClouds[entry][0] + " " + rawClouds[entry][1]
  return prettyClouds

def buildHtml(inputData):
  mytemplate = Template(filename=htmlTemplate)
  location=inputData[1]
  localcurtime=convertTime(inputData[2])['local']
  zulucurtime = convertTime(inputData[2])['zulu']
  conditions=inputData[30]
  wind=makeWind(inputData[7],inputData[8],inputData[9])
  temperature=convertTemp(inputData[5])
  dewpoint=convertTemp(inputData[6])
  altimeter=round(float(inputData[11]), 2)
  vis = inputData[10]
  rawClouds = {'layer1': [inputData[22],inputData[23]],
            'layer2': [inputData[24],inputData[25]],
            'layer3': [inputData[26],inputData[27]],
            'layer4': [inputData[28],inputData[29]]
           }
  myClouds = buildClouds(rawClouds)
  renderedData = mytemplate.render(
    airport=location,
    tztime=localcurtime,
    ztime=zulucurtime,
    conditions=conditions,
    wind=wind,
    temperature=temperature,
    dewpoint=dewpoint,
    altimeter=altimeter,
    visibility = vis,
    clouds = myClouds)
  return renderedData

def saveHtml(data, airport):
  # fileToSave = path of the file to save
  fileToSave = sysinforSaveDir + "/" + airport + ".html"
  # Check to see if the save dir exists and create if not
  if not os.path.exists(sysinforSaveDir):
    os.makedirs(sysinforSaveDir)
  # Open, trunacate, write, close
  saveFile = open(fileToSave, "w")
  saveFile.truncate()
  saveFile.write(data)
  saveFile.close()

airportList = ['KDTO', 'KAFW', 'KSYI']
wxDataList = getWxFromFile()
for x in airportList:
  airportWx = getAirportWx(wxDataList, x)
  if airportWx:
    renderedData = buildHtml(airportWx)
    saveHtml(renderedData, x)
  else:
    print "Error"
