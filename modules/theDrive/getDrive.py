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
rntsAddy = ["parents","115 Park Lane Trophy Club Tx"]
tdtoAddy = ["Denton Airport","5000 Airport Rd Denton TX"]
googApi = "AIzaSyDg5cmsPRKv2BqH889-y1AS8Y2r-de9McU"

mainDir = "/Users/bob/work/sysinfor/modules/theDrive"
htmlBaseDir = mainDir + "/html"
templateDir = htmlBaseDir + "/templ"
htmlSaveDIr = htmlBaseDir + "/sysinfor"
htmlTemplate = templateDir + "theDrive.template"

import requests

def buildPayload(destin):
    payload = {'origin' : homeAddy,
               'destination' : destin,
               'avoid' : 'tolls',
               'key' : googApi
               }
    return payload

def getData(payload):
    r = requests.get(URL,params=payload)
    return r

def processData(information):
    inforDict = information.json()
    distance = infoStruct['routes'][0]['legs'][0]['distance']['text']
    time = infoStruct['routes'][0]['legs'][0]['duration']['text']
    distTime = {'dist': distance,'tme': time}
    return destTime

def buildHtmlData(infoStruct):



destList = [workAddy,rntsAddy,tdtoAddy]

for dest in destList:
    payload = buildPayload(dest)
    informs = getData(payload)
    dataPro = processData(informs)
    theHtml = buildHtmlData(dataPro)
