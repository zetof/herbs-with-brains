#!/usr/bin/python
# -*- coding: utf-8 -*-

# Import des librairies
import struct
from time import time, sleep, strftime
from serial import SerialException
from talk import Talk
from menu import Menu
from params import Params
from threading import Lock

# Définition du nom de l'unité VERT-X
uuid = '26777312-ec5d-11e6-9bfe-0013ef602d58'

# Définition du logger
LOGGER = 'vertx.logger'

# Définition de la langue d'usage
LOCALE = 'fr-FR'

# Définition des propriétés de communication série avec les Arduinos
ARD1 = 'ARD1'
ARD1_PORT = '/dev/ard1'
ARD2 = 'ARD2'
ARD2_PORT = '/dev/ttyUSB0'
ARD_SPEED = 115200

# Définition des paramètres de configuration pour les services internet
HTTP_BASE_URL = 'https://vertx.zetof.net'
HTTP_USER = 'vertx'
HTTP_PWD = 'LeVertCaGere'

# Définition du lock pour la lecture des threads provenant des Arduinos
aLock = Lock()

# Flag décidant si le système doit continuer de tourner ou s'arrêter
running = True

# Fonction qui traite des problèmes de lecture sur le port USB d'un Arduino
#
def arduinoReadProblem(data):

	# Raté ponctuel à la lecture du bus USB venant d'un Arduino
	#
	if data[1] == 'ARDUINO_READ_WARNING':
		talk.log(talk.WARNING, ['warning.usb.arduino.read.ko', data[0]])

	# Déconnexion totale d'un Arduino
	#
	elif data[1] == 'ARDUINO_READ_ALERT':

		# Déconnexion - Première valeur du message = SET
		if data[2] == 'SET':
			talk.setAlarm(talk.CRITICAL, ['alert.usb.arduino.read.ko', data[0]], aAction = data[0] + ':' + data[1])

		# Reconnexion - Première valeur du message = RESET
		elif data[2] == 'RESET':
			talk.resetAlarm(['info.usb.arduino.read.ok', data[0]], aAction = data[0] + ':' + data[1])

# Fonction qui imprime sur l'écran LCD les données reçues sur le port USB d'un Arduino
#
def processKey(data):

	# Le flag running peut être affecté par le menu car on peut décider de quitter le système
	global running

	# Si le rétro-éclairage de l'écran LCD est éteint, on affiche le statut du système, on le rallume et on réinitialise la position dans le menu
	if talk.lcd.isBacklightOn() == False:
		talk.lcd.printMessage(talk.i18n.t('menu.system.idle', [strftime('%Y-%m-%d %H:%M:%S')]))

	# Sinon on traite la touche normalement
	else:

		# On récupère la possible action à effectuer
		action = menu.getAction(data[2])

		# Si il y a une action à affectuer, on l'éxécute, sinon on ne fait rien
		if action != None:

			# On commence par l'affichage du menu
			# Par défaut, on estime qu'il n'y a pas de valeur à insérer dans l'affichage du menu
			value = []

			# Sauf pour les éléments de menu suivants:
			if action == 'menu.air.temperature':
				value = [params.getParameterAsString(params.AIR_TEMPERATURE)]
			elif action == 'menu.air.humidity':
				value = [params.getParameterAsString(params.AIR_HUMIDITY)]

			# On affiche l'élément de menu
			talk.lcd.printMessage(talk.i18n.t(action, value))

			# Si on doit prendre une action suite à un élément de menu, on vérifie dans cette partie de code
			if action == 'menu.shutdown.ongoing':
				running = False
			
# Fonction qui sauvegarde un paramètre renvoyé par un des Arduinos
#
def setParameter(data):

	# On vérifie le nom du paramètre à enregistrer et on stocke la valeur renvoyée
	if data[1] == 'AIR_TEMP':
		params.setParameterValue(params.AIR_TEMPERATURE, data[2])
	elif data[1] == 'AIR_HUM':
		params.setParameterValue(params.AIR_HUMIDITY, data[2])

# Définition du callback lors de la réception d'un message venant d'un Arduino
# Ce callback prend en compte l'analyse des messages venant d'un Arduino et
# l'action associée
#
def processDataFromArduino(receivedData):

	# On est dans une portion critique donc on s'approprie cette portion de programme
	aLock.acquire()
	try:

		# On sépare les parties du message reçu
		splitData = receivedData.split(':')

		# On définit un dictionnaire pour le traitement des différents messages
		action = {'ARDUINO_READ_WARNING': arduinoReadProblem,
							'ARDUINO_READ_ALERT': arduinoReadProblem,
							'KEY': processKey,
							'AIR_TEMP': setParameter,
							'AIR_HUM': setParameter}	
	
		# Finalement, on appelle la fonction correspondante à la commande sur base du dictionnaire
		# Si la clé n'existe pas, il est nécessaire d'intercepter l'erreur pour éviter tout problème
		# En cas de problème, on le reporte dans les logs
		try:
			action[splitData[1]](splitData)

		except KeyError as e:
			talk.log(Talk.WARNING, ['warning.usb.command.not.found', e, splitData[0]])

	# On quitte la portion critique donc on relache le lock
	finally:
		aLock.release()

# Définition du callback lors de la réception d'un message venant d'internet
# Ce callback prend en compte l'analyse des messages venant d'internet et
# l'action associée
#
def processDataFromInternet(receivedData):

	print receivedData

# Initialisation de l'objet global de communication
talk = Talk(LOGGER, LOCALE, HTTP_BASE_URL, HTTP_USER, HTTP_PWD, processDataFromInternet)

# On connecte les Arduinos au Raspberry
talk.addArduino(ARD1, ARD1_PORT, ARD_SPEED, processDataFromArduino)
talk.addArduino(ARD2, ARD2_PORT, ARD_SPEED, processDataFromArduino)

# On initialise les paramètres sous contrôle de l'unité
params = Params()

# On initialise les éléments de menu
menu = Menu()

# On fait tourner le programme un moment
while running == True:
	try:
		talk.sendArduino(ARD2, 'RGB', [255, 0, 0])
		sleep(5)
		talk.sendArduino(ARD2, 'RGB', [0, 0, 0])
		sleep(5)
	except SerialException as e:
		talk.log(talk.WARNING, ['warning.usb.arduino.write.ko', ARD2])

# On fait le ménage à la sortie de la boucle principale, avant d'aller faire dodo
talk.stop()
