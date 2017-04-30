#!/bin/env python

# Home to work
# https://maps.googleapis.com/maps/api/directions/json?origin=901+Clearview+Dr+Bedford+Tx&destination=111+Customer+Way+Irving+Tx&avoid=tolls&key=AIzaSyDg5cmsPRKv2BqH889-y1AS8Y2r-de9McU

# Home to parents
# https://maps.googleapis.com/maps/api/directions/json?origin=901+Clearview+Dr+Bedford+Tx&destination=115+park+lane+trophy+club+tx&avoid=tolls&key=AIzaSyDg5cmsPRKv2BqH889-y1AS8Y2r-de9McU

# Store normal addresses
# Process
# Build html
# iFrame each one

URL = "https://maps.googleapis.com/maps/api/directions/json"
homeAddy = ["Home","901 Clear View Dr Bedford Tx"]
workAddy = ["Work","111 Customer Way Irving Tx"]
rntsAddy = ["Parents","115 Park Lane Trophy Club Tx"]
tdtoAddy = ["Denton Airport","5000 Airport Rd Denton TX"]
googApi = "AIzaSyDg5cmsPRKv2BqH889-y1AS8Y2r-de9McU"

mainDir = "/Users/bob/work/sysinfor/modules/theDrive"
htmlBaseDir = mainDir + "/html"
templateDir = htmlBaseDir + "/templ"
htmlSaveDir = htmlBaseDir + "/sysinfor"
htmlTemplate = templateDir + "/" + "theDrive.template"

import requests
from mako.template import Template
import os

def buildPayload(destin):
    payload = {'origin' : homeAddy[1],
               'destination' : destin[1],
               'avoid' : 'tolls',
               'key' : googApi
               }
    return payload

def getData(payload):
    r = requests.get(URL,params=payload)
    return r

def processData(information):
    infoStruct = information.json()
    distance = infoStruct['routes'][0]['legs'][0]['distance']['text']
    time = infoStruct['routes'][0]['legs'][0]['duration']['text']
    route = infoStruct['routes'][0]['summary']
    distTime = {'dist': distance,'time': time,'route': route}
    return distTime

def buildHtmlData(infoStruct,destination):
    mytemplate = Template(filename=htmlTemplate)
    time = infoStruct['time']
    distance = infoStruct['dist']
    route = infoStruct['route']
    renderedData = mytemplate.render(
        to=destination[0],
        route=route,
        froma=homeAddy[0],
        distance=distance,
        time=time)
    print renderedData
    return renderedData

def saveHtml(html,dest):
    fileToSave = htmlSaveDir + "/" + dest[0] + ".html"
    # Check to see if the save dir exists and create if not
    if not os.path.exists(htmlSaveDir):
      os.makedirs(htmlSaveDir)
    # Open, trunacate, write, close
    saveFile = open(fileToSave, "w")
    saveFile.truncate()
    saveFile.write(html)
    saveFile.close()


destList = [workAddy,rntsAddy,tdtoAddy]

for dest in destList:
    payload = buildPayload(dest)
    informs = getData(payload)
    dataPro = processData(informs)
    theHtml = buildHtmlData(dataPro,dest)
    saveHtml(theHtml,dest)
