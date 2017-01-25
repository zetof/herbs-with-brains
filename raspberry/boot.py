#!/usr/bin/python
# -*- coding: utf-8 -*-

# Import des librairies
import time
import struct
from usb import USBDaemon
from talk import Talk

# Définition des propriétés de communication série avec les Arduinos
ARD1 = 'ARD1'
ARD1_PORT = '/dev/ard1'
ARD2 = 'ARD2'
ARD2_PORT = '/dev/ttyUSB0'
ARD_SPEED = 115200

# Fonction qui traite des problèmes de lecture sur le port USB d'un Arduino
#
def arduinoReadProblem(data):

	# Raté à la lecture du bus USB venant d'un Arduino
	#
	if data[1] == 'ARDUINO_READ_WARNING':
		talk.setAlarm(talk.WARNING, data[0] + ':' + data[1], ['warning.usb.arduino.read.ko', data[0]], False)

	# Déconnexion totale d'un Arduino
	#
	elif data[1] == 'ARDUINO_READ_ALERT':

		# Déconnexion - Première valeur du message = SET
		if data[2] == 'SET':
			talk.setAlarm(talk.CRITICAL, data[0] + ':' + data[1], ['alert.usb.arduino.read.ko', data[0]], True)

		# Reconnexion - Première valeur du message = RESET
		elif data[2] == 'RESET':
			talk.resetAlarm(['info.usb.arduino.read.ok', data[0]], aAction = data[0] + ':' + data[1])

# Fonction qui imprime sur l'écran LCD les données reçues sur le port USB d'un Arduino
#
def processKey(data):
	print(data[0] + ':' + data[1] + ':' + data[2])

# Fonction qui imprime sur l'écran LCD les données reçues sur le port USB d'un Arduino
#
def printData(data):
	print(data[0] + ':' + data[1] + ':' + data[2])
	talk.lcd.clear()
	talk.lcd.printAt(0, 0, data[2])
	talk.lcd.backlightDelay()

# Définition du callback lors de la réception d'un message venant d'un Arduino
# Ce callback prend en compte l'analyse des messages venant d'un Arduino et
# l'action associée
#
def processDataFromArduino(receivedData):

	# On sépare les parties du message reçu
	splitData = receivedData.split(':')

	# On définit un dictionnaire pour le traitement des différents messages
	action = {'ARDUINO_READ_WARNING':arduinoReadProblem,
						'ARDUINO_READ_ALERT':arduinoReadProblem,
						'KEY':processKey,
						'AIR_TEMP':printData,
						'AIR_HUM':printData}	
	
	# Finalement, on appelle la fonction correspondante à la commande sur base du dictionnaire
	action[splitData[1]](splitData)

# Initialisation de l'objet global de communication
talk = Talk('vertx.logger')

# On connecte les Arduinos au Raspberry
talk.addArduino(ARD1, ARD1_PORT, ARD_SPEED, processDataFromArduino)
talk.addArduino(ARD2, ARD2_PORT, ARD_SPEED, processDataFromArduino)

# On fait tourner le programme un moment
time.sleep(60)

# On fait le ménage à la sortie de la boucle principale, avant d'aller faire dodo
talk.stop()
