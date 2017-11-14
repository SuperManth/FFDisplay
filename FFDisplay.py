#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Dieses Script soll die Daten von einem Digitalmelder der Feuerwehr auslesen
# und dann in einer MySQL-Datenbank speichern.
# Zusätzlich wird eine Logdatei geführt.
# Die Daten des Melders werden am Serielport empfangen.
# Copyright Feuerwehr Appen
# ß=\xdf

import os, sys, time, datetime, serial, requests
import RPi.GPIO as GPIO
import mysql.connector as mysqlcon

# Konstaten Einstellungen
COM_PORT = "/dev/ttyUSB0"
DATABASE = "FFDisplay"
DBUSER = "test"
DBPASSWORD = "test"
DBHOST = "localhost"
SEND_PIN = 3
FF_LAT = "53.66315"
FF_LNG = "9.732960"
VERSION = "2017-11-14-002"
SteckdosenEinAus = 0
EINSCHALTZEIT = 1800
ABSCHALTZEIT = 1200

# Steckdosen Einstellungen
DOSEMEIN = "S10101001100110011001101001010101101010101010101010100101101010010"
DOSEMAUS = "S10101001100110011001101001010101101010101010101010100110101010010"
DOSE1EIN = "S10101001100110011001101001010101101010101010101010101001101010010"
DOSE1AUS = "S10101001100110011001101001010101101010101010101010101010101010010"
DOSE2EIN = "S10101001100110011001101001010101101010101010101010101001101001100"
DOSE2AUS = "S10101001100110011001101001010101101010101010101010101010101001100"
DOSE3EIN = "S10101001100110011001101001010101101010101010101010101001101001010"
DOSE3AUS = "S10101001100110011001101001010101101010101010101010101010101001010"
on_delay = 0.00018
start_delay = 0.00266
short_delay = 0.00033
long_delay = 0.00136
extended_delay = 0.01020
NUM_ATTEMPTS = 10

add_Status = ("INSERT INTO tabEinsatz "
				"(Datum, Alarmierung, Stichwort, InfoText, Ort, Strasse, Adresse2, Name, Feld07, ZusatzInfo, Person, Feld10, Feld11, Feld12, Feld13, Feld14, EinsatzNr, Sonderrechte, lat, lng) "
				"VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)")
				
# Google Maps
def G_Maps(liste):
	if str(liste[3]) == "" and str(liste[4]) == "":
		LogSchreiben("Googlemaps Adresse leer")
		return False
		
	GOOGLE_MAPS_API_URL = 'http://maps.googleapis.com/maps/api/geocode/json'
	params = {
		'address': str(liste[4])+", "+str(liste[3])+", Germany",
		'sensor': 'false',
		'region': 'de'
	}
	
	# Do the request and get the response data
	req = requests.get(GOOGLE_MAPS_API_URL, params=params)
	res = req.json()
	
	# Use the first result
	if str(res['status']) == "OK":
		result = res['results'][0]
		geodata = dict()
		geodata['lat'] = result['geometry']['location']['lat']
		geodata['lng'] = result['geometry']['location']['lng']
		geodata['address'] = result['formatted_address']
		return geodata['lat'],geodata['lng']
	elif str(res['status']) == "OVER_QUERY_LIMIT":
		LogSchreiben("Googlemaps erster durchgang")
		LogSchreiben("Googlemaps fehler: " + str(res['status']))
		LogSchreiben("Googlemaps Strasse: " + str(liste[4]))
		LogSchreiben("Googlemaps Ort: " + str(liste[3]))
		time.sleep(2)
		
		req = requests.get(GOOGLE_MAPS_API_URL, params=params)
		res = req.json()
		if str(res['status']) == "OK":
			LogSchreiben("Googlemaps zweiter durchgang OK")
			result = res['results'][0]
			geodata = dict()
			geodata['lat'] = result['geometry']['location']['lat']
			geodata['lng'] = result['geometry']['location']['lng']
			geodata['address'] = result['formatted_address']
			return geodata['lat'],geodata['lng']
		else:
			LogSchreiben("Googlemaps zweiter durchgang")
	LogSchreiben("Googlemaps fehler: " + str(res['status']))
	LogSchreiben("Googlemaps Strasse: " + str(liste[4]))
	LogSchreiben("Googlemaps Ort: " + str(liste[3]))
	return False

def LogSchreiben(LogText):
	LogDatei='FFDisplay.log'
	logfile = open(LogDatei, "a", encoding="utf-8", errors='replace')
	logfile.write(str(datetime.datetime.now()) + " -> " + LogText + '\n')
	logfile.close

def CheckNewStatus():
	return os.path.isfile('./ffstatus.txt')

def ConnectDB():
	try:
		connection = mysqlcon.connect(host=DBHOST, user=DBUSER, passwd=DBPASSWORD, db=DATABASE)
	except mysqlcon.Error as e:
		LogSchreiben("Datenbank Fehler. " + str(e))
		print("Datenbank Fehler. " + str(e))
		return False
	else:
		return connection

def StatusListe(StText):
	Liste = []
	offset = 2
	endpos = StText.find("*")
	while endpos != -1:
		Liste.append(StText[offset:endpos])
		offset = endpos + 1
		endpos = StText.find("*",endpos + 1)
	return Liste
	
def DatenSpeichern(liste,geo_lat,geo_lng):
	einsatzdaten = (datetime.datetime.date(datetime.datetime.today()), liste[0], liste[1], liste[2], liste[3], liste[4], liste[5], liste[6], liste[7], liste[8], liste[9], liste[10], liste[11], liste[12], liste[13], liste[14], liste[15], liste[16], geo_lat, geo_lng)
	connect = ConnectDB()
	cursor = connect.cursor()
	try:
		cursor.execute(add_Status,einsatzdaten)
	except mysqlcon.Error as e:
		LogSchreiben("SQL Fehler. " + str(e))
		print("SQL Fehler. " + str(e))
	else:
		LogSchreiben("Tabelle gefuellt")
	connect.commit()
	cursor.close
	connect.close

def ZeichenErsetzen(StText,Leerzeichen):
	Text = ""
	if Leerzeichen:
		Zeichen = "-"
		PlusZeichen = 1
	else:
		Zeichen = "\\"
		PlusZeichen = 4
	offset = 0
	endpos = StText.find(Zeichen)
	while endpos != -1:
		Text = Text + StText[offset:endpos]
		ZeichenKette = StText[endpos:endpos + PlusZeichen]
		if Leerzeichen:
			Text = Text + " "
		else:
			if str(ZeichenKette) == "\\xdf":
				Text = Text + chr(0xdf)
			elif str(ZeichenKette) == "\\xfc":
				Text = Text + chr(0xfc)
			elif str(ZeichenKette) == "\\xf6":
				Text = Text + chr(0xf6)
			elif str(ZeichenKette) == "\\xe4":
				Text = Text + chr(0xe4)
			elif str(ZeichenKette) == "\\xd6":
				Text = Text + chr(0xd6)
			else:
				if str(ZeichenKette) != "\\r\\n": 
					LogSchreiben("Zeichenkette noch nicht definiert: " + ZeichenKette)
		offset = endpos + PlusZeichen
		endpos = StText.find(Zeichen,endpos + PlusZeichen)
	endpos = len(StText)
	Text = Text + StText[offset:endpos]
	return Text
	
def DosenEin():
	LogSchreiben("Steckdosen einschalten")
	transmit_code(DOSEMEIN)
	# transmit_code(DOSE1EIN)
	# transmit_code(DOSE2EIN)
	# transmit_code(DOSE3EIN)
	# GPIO.output(SEND_PIN, 1)
	
def DosenAus():
	LogSchreiben("Steckdosen ausschalten")
	transmit_code(DOSEMAUS)
	# transmit_code(DOSE1AUS)
	# transmit_code(DOSE2AUS)
	# transmit_code(DOSE3AUS)
	# GPIO.output(SEND_PIN, 0)
	
def transmit_code(code):
	'''Transmit a chosen code string using the GPIO transmitter'''
	for t in range(NUM_ATTEMPTS):
		for i in code:
			if i == 'S':
				GPIO.output(SEND_PIN, 1)
				time.sleep(on_delay)
				GPIO.output(SEND_PIN, 0)
				time.sleep(start_delay)
			elif i == '1':
				GPIO.output(SEND_PIN, 1)
				time.sleep(on_delay)
				GPIO.output(SEND_PIN, 0)
				time.sleep(short_delay)
			elif i == '0':
				GPIO.output(SEND_PIN, 1)
				time.sleep(on_delay)
				GPIO.output(SEND_PIN, 0)
				time.sleep(long_delay)
			else:
				continue
		GPIO.output(SEND_PIN, 0)
		time.sleep(extended_delay)
	
# Hauptprogramm----------------------------------------------------

LogSchreiben("Start" + str(sys.argv) + " >> " + VERSION)
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(SEND_PIN, GPIO.OUT)
GPIO.output(SEND_PIN, 0)
LetzterVersuch_time = datetime.datetime.now()
if len(sys.argv) > 1:
	if sys.argv[1] == '-install':
		LogSchreiben("Installieren")
		print("Verbindung zum Host herstellen")
		try:
			db = mysqlcon.connect(host="localhost", user="root", passwd="", db="****")
		except mysqlcon.Error as e:
			LogSchreiben("Host Verbindungsfehler" + str(e))
			print("Host Verbindungsfehler " + str(e))
		else:
			LogSchreiben("Datenbank erstellen")
			print("Datenbank erstellen")
			db1 = db.cursor()
			try:
				db1.execute('CREATE DATABASE ' + DATABASE)
			except mysqlcon.Error as e:
				LogSchreiben("Datenbank CREATE-Fehler. " + str(e))
				print("Datenbank CREATE-Fehler. " + str(e))
			else:
				sql_command="""
				CREATE TABLE tabEinsatz (
				ID INTEGER PRIMARY KEY AUTO_INCREMENT,
				Datum DATE,
				Alarmierung VARCHAR(50),
				Stichwort VARCHAR(50),
				InfoText VARCHAR(200),
				Ort VARCHAR(100),
				Strasse VARCHAR(100),
				Adresse2 VARCHAR(200),
				Name VARCHAR(100),
				Feld07 VARCHAR(200),
				ZusatzInfo VARCHAR(200),
				Person VARCHAR(200),
				Feld10 VARCHAR(200),
				Feld11 VARCHAR(200),
				Feld12 VARCHAR(200),
				Feld13 VARCHAR(200),
				Feld14 VARCHAR(200),
				EinsatzNr VARCHAR(20),
				Sonderrechte VARCHAR(20),
				lat FLOAT(10,6),
				lng FLOAT(10,6));"""
				LogSchreiben("Tabelle erstellen")
				print("Tabelle erstellen")
				try:
					db1.execute(sql_command)
				except mysqlcon.Error as e:
					LogSchreiben("SQL Fehler. " + str(e))
					print("SQL Fehler. " + str(e))
				else:
					LogSchreiben("Tabelle erstellt")
					print("Tabelle erstellt")
					db.commit()
				db1.close()
			db.close()
else:
	connect = ConnectDB()
	if connect == False:
		print("Bitte Datenbank anlegen!")
	else:
		connect.close()
		ser = serial.Serial()
		ser.baudrate = 9600
		ser.port = COM_PORT
		ser.timeout =1
		try:
			ser.open()
		except:
			LogSchreiben("Comport konnte nicht geoeffnet werden!")
			LogSchreiben(str(ser))
		else:
			LogSchreiben("Comport geoeffnet")
		
		while ser.is_open:
			text_empfang = ser.readlines()
			if len(text_empfang) > 1 or CheckNewStatus():
				if CheckNewStatus():
					LogSchreiben("Neue Datei gefunden")
					statusfile=open('./ffstatus.txt','r',encoding='utf-8',errors='ignore')
					text_datei=statusfile.readline()
					statusfile.close()
					os.remove('./ffstatus.txt')
					txtempfang = str(text_datei)
				else:
					LogSchreiben("Schnittstelle gelesen")
					txtempfang = ""
					for i in range(0,len(text_empfang)):
						if str(text_empfang[i]).find("*")!= -1:
							txtempfang=str(text_empfang[i])
							break
				LogSchreiben("Empfangen: " + str(txtempfang))
				txtempfang=ZeichenErsetzen(str(txtempfang),False)
				Liste=StatusListe(txtempfang)
				if len(Liste) == 17:
					Liste[3] = ZeichenErsetzen(Liste[3],True)
					DatenGoogle = G_Maps(Liste)
					if DatenGoogle:
						DatenSpeichern(Liste,str(DatenGoogle[0]),str(DatenGoogle[1]))
					else:
						DatenSpeichern(Liste,FF_LAT,FF_LNG)
					beginning_time = datetime.datetime.now()
					DosenEin()
					SteckdosenEinAus = 1
			if SteckdosenEinAus:
				time_delta = datetime.datetime.now() - beginning_time
				cumulative_time = time_delta.seconds
				if cumulative_time > EINSCHALTZEIT:
					DosenAus()
					SteckdosenEinAus = 0
					LetzterVersuch_time = datetime.datetime.now()
			else:
				time_delta = datetime.datetime.now() - LetzterVersuch_time
				cumulative_time = time_delta.seconds
				if cumulative_time > ABSCHALTZEIT:
					DosenAus()
					LetzterVersuch_time = datetime.datetime.now()
		ser.close()
GPIO.cleanup()
LogSchreiben("Ende")

