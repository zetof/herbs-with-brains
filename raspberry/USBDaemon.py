#!/usr/bin/python
# -*- coding: utf-8 -*-

import threading
import serial

# Classe implémentant la communication série entre le Raspberry et les Arduinos sur un port USB
#
class USBDaemon:


	# Liste des constantes
	#
	READ_TIME = 0.1	# Durée entre deux lectures du port USB en secondes

	# Méthode qui tourne constamment en thread, lancée par le constructeur
	# Ecoute le port USB en provenance de l'Arduino
	# Si une communication est détectée, les données sont dispatchées aux observateurs de la classe
	#
	def __listenUSB(self):

		# On ne reprogramme l'écoute du port USB que si le programme principal n'a pas demandé un arrêt général
		if self.running == True:

			# On ne lit que si des données sont présentes
			if self.arduino.inWaiting() > 0:
				self.messageReceived = self.arduino.readline().strip()

				# On envoie ce qui a été lu à tous les callbacks enregistrés
				for fn in self.callbacks:
					fn(self.messageReceived)

			# Finalement, on reboucle pour continuer d'écouter le port USB jusqu'à la fin du programme
			readTimer = threading.Timer(self.READ_TIME, self.__listenUSB)
			readTimer.start()

	# Méthode permettant d'enregistrer une fonction externe en callback de la réception d'un message
	#
	def subscribe(self, callback):
		self.callbacks.append(callback)

	# Méthode permettant d'arrêter de façon propre la classe par arrêt programmé des threads
	#
	def stop(self):
		self.arduino.close()
		self.running = False

	# Constructeur de la classe. Ce constructeur prend en entrée les paramètres suivants:
	#		* serialName: le nom du port USB à utiliser pour la communication (ex: /dev/ttyACM0)
	#		* serialSpeed: la vitesse de communication en bauds
	#
	def __init__(self, serialName, serialSpeed):

		# Crée l'objet de communication avec les valeurs d'initialisation
		self.arduino = serial.Serial(serialName, serialSpeed)

		# Création des variables de contôle de la classe
		self.callbacks = []
		self.messageReceived = None
		self.running = True

		# Démarre l'écoute du port série
		self.__listenUSB()
