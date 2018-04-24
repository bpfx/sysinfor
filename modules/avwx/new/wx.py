#!/usr/bin/env python

import requests
import gzip
import csv
from datetime import datetime
from dateutil import tz
import boto3
from decimal import *

from_zone = tz.gettz('Zulu')
to_zone = tz.gettz('America/Chicago')


# Setup where everything is
# mainDir: Where the module lives
#   todo: when sysinfor is further along, might make this one of those cool
#         auto-finding-where-everything-is-dynamically-in-a-pythony-way-things
mainDir = "/home/ec2-user/work/newAvWx"

# wxDir: where the wx csv lives
# Currently:
# /Users/bob/work/sysinfor/modules/avwx/wx/metars.cache.csv
wxDir = mainDir + "/data"
wxFile = wxDir + "/" + "metars.cache.csv"
wxFileGz = wxFile + ".gz"
wxRemoteFile = "https://aviationweather.gov/adds/dataserver_current/current/metars.cache.csv.gz"

db = boto3.resource('dynamodb')
table = db.Table('avWxMetar')

def setupStuff():
  r = requests.get(wxRemoteFile,stream=True)
  with open(wxFileGz,"wb") as f:
    for chunk in r.iter_content(chunk_size=1024):
      if chunk:
          f.write(chunk)
  f.close()
  with gzip.open(wxFileGz,"rb") as f:
      file_content = f.read()
  f.close()
  with open(wxFile,"wb") as f:
    f.write(file_content)
  f.close()

# WRite out what this function does
def getWxFromFile():
  with open(wxFile, 'rb') as csvFile:
    reader = csv.reader(csvFile)
    wxList = list(reader)
    return wxList

def getAirportWx(theList,airport):
  for line in theList:
    if len(line) > 1:
      if line[1] == airport:
        return line
  return None

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
  if gust != "":
    theWind = direction + "&#176" + " @ " + speed + "kts" + "G" + gust + "kts"
  else:
      theWind = direction + "&#176" + " @ " + speed + "kts"
  return theWind

def buildClouds(rawClouds):
  prettyClouds = {}
  layerList = ['layer1','layer2','layer3','layer4']
  for entry in layerList:
    if rawClouds[entry][0] != "":
      prettyClouds[entry] = rawClouds[entry][0] + " " + rawClouds[entry][1]
  return prettyClouds

def buildHtml(inputData):
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
  renderedData = {
  "identifier":location,
  "tztime":localcurtime,
  "ztime":zulucurtime,
  "conditions":conditions,
  "wind":wind,
  "temperature":Decimal(str(temperature)),
  "dewpoint":Decimal(str(dewpoint)),
  "altimeter":Decimal(str(altimeter)),
  "visibility":vis,
  "clouds":myClouds
  }
  return renderedData

def writeToDB(data):
  table.put_item(Item=data)

if __name__ == "__main__":
  #setupStuff()
  airportList = ['KDTO', 'KAFW', 'KSYI']
  wxDataList = getWxFromFile()
  renderedData = []
  for x in airportList:
    airportWx=getAirportWx(wxDataList, x)
    retdata = buildHtml(airportWx)
    renderedData.append(retdata)
    writeToDB(retdata)
    print table.get_item(Key={'identifier':x})
