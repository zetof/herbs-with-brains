#!/r/bin/python
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

# Définition du callback lors de la réception d'un message venant d'un Arduino
# Ce callback prend en compte l'analyse des messages venant d'un Arduino et
# l'action associée
#
def processDataFromArduino(receivedData):

	# On sépare les parties du message reçu en machine, commande et valeurs (si il y en a au moins une)
	msgParts = receivedData.split(':')
	machine = msgParts[0]
	command = msgParts[1]
	if len(msgParts) > 2:
		values = msgParts[2:]

	# On traite le message reçu par rapport à la commande
	if command == 'READ_WARNING':
		talk.setAlarm(talk.WARNING, 'Erreur de lecture sur: ' + machine, False)
	elif command == 'READ_ALERT':
		if values[0] == 'SET':
			talk.setAlarm(talk.CRITICAL, 'Perte de connxion permanente sur: ' + machine, True, aKey = machine + ':' + command)
		elif values[0] == 'RESET':
			talk.resetAlarm(machine + ':' + command, 'Reprise de la communication sur: ' + machine)
	
	print(receivedData)
	talk.lcd.clear()
	talk.lcd.printAt(0, 0, receivedData)
	talk.lcd.backlightDelay()

# Initialisation de l'objet global de communication
talk = Talk('vertx.logger')

# On connecte les Arduinos au Raspberry
talk.addArduino(ARD1, ARD1_PORT, ARD_SPEED, processDataFromArduino)
talk.addArduino(ARD2, ARD2_PORT, ARD_SPEED, processDataFromArduino)

# On fait tourner le programme un moment
time.sleep(30)

# On fait le ménage à la sortie de la boucle principale, avant d'aller faire dodo
talk.stop()
