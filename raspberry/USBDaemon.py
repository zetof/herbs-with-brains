#!/usr/bin/python
# -*- coding: utf-8 -*-

import time
import threading
import serial

# Classe implémentant la communication série entre le Raspberry et les Arduinos sur un port USB
#
class USBDaemon:


	# Liste des constantes
	#
	READ_TIME = 0.1						# Durée entre deux lectures du port USB en secondes
	RECONNECT_TIME = 5				# Durée entre deux tentatives de reconnexion
	NBR_OF_RECONNECTIONS = 3	# Nombre de tentatives de reconnexion avant la levée d'une alarme

	# Méthode qui tourne constamment en thread, lancée par le constructeur
	# Ecoute le port USB en provenance de l'Arduino
	# Si une communication est détectée, les données sont dispatchées aux observateurs de la classe
	#
	def __listenUSB(self):

		# On initialise les variables portant les clés des éventuelles WARNING ou ALERT
		warningKey = None
		alertKey = None

		# On ne reprogramme l'écoute du port USB que si le programme principal n'a pas demandé un arrêt général
		if self.running == True:

			# On ne lit que si des données sont présentes
			try:
				if self.arduino.inWaiting() > 0:
					self.messageReceived = self.arduino.readline().strip()

					# On appelle les callbacks
					for fn in self.callbacks:
						fn(self.messageReceived)

			# On a un incident à la lecture du port USB
			except IOError as e:

				# On rapporte l'incident au système et on initialise la reconnexion
				warningKey = self.warningCallback(e, True, False)
				reconnectCounter = 0
				reconnected = False

				# Tant qu'on n'a pas réussi une reconnexion, on essaie, à condition que le programme est toujours en cours
				# Chaque fois que l'on est arrivé au nombre maximum d'essais, on remonte une ALERT
				while reconnected == False and self.running == True:

					# Tentative de reconnexion - On ferme d'abord le port USB
					# Si on y arrive, on le signale afin de sortir de la boucle
					try:
						self.arduino.close()
						time.sleep(self.RECONNECT_TIME)
						self.__openUSB()
						reconnected = True

					# Echec à la tentative de reconnexion - On incrémente le compteur des essais
					except serial.SerialException as e:
						reconnectCounter += 1

						# Si le nombre maximum de reconnexion est atteint, on rapporte l'incident en ALERT
						if reconnectCounter == self.NBR_OF_RECONNECTIONS:

							# On supprime le WARNING avant de passer en ALERT
							self.clearAlarmCallback(warningKey, False)
							warningKey = None

							# Si l'alarme n'est pas encore en niveau ALERT, on le fait passer et on enclenche le panneau des alarmes
							if alertKey == None:
								alertKey = self.alertCallback(e, True, False)

							# Sinon, on ne fait qu'enregistrer une nouvelle entrée dans le log
							else:
								alertKey = self.alertCallback(e, False, False)

							# On réinitialise le compteur des essais pour relancer une tentative
							reconnectCounter = 0

			# Si on ressort d'une boucle de déconnexion, c'est qu'on a réussi à se reconnecter
			# Il est donc nécessaire de supprimer l'ALERT avant de continuer
			if warningKey != None:
				self.clearAlarmCallback(warningKey, False)
			elif alertKey != None:
				self.clearAlarmCallback(alertKey, 'La communication sur le port USB a repris')
				alertKey = None
			
			# Finalement, on reboucle pour continuer d'écouter le port USB jusqu'à la fin du programme
			readTimer = threading.Timer(self.READ_TIME, self.__listenUSB)
			readTimer.start()

	# Méthode permettant la connexion au port USB
	#
	def __openUSB(self):

		# On essaie de créer l'objet de communication avec les valeurs d'initialisation
		try:
			self.arduino = serial.Serial(self.serialName, self.serialSpeed)

		# Si on n'y arrive pas, on remonte une exception
		except serial.SerialException as e:
			raise e
		
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
	#		* warningCallback: la fonction à exécuter en cas d'alarme de type WARNING
	#		* alertCallback: la fonction à exécuter en cas d'alarme de type ALERT
	#		* clearAlarmCallback: la fonction à exécuter en cas de suppression d'une alarme en cours
	#
	def __init__(self, serialName, serialSpeed, warningCallback, alertCallback, clearAlarmCallback):

		try:

			# On sauvegarde les valeurs d'initialisation si on doit redémarrer la communication
			# après une erreur survenue sur le port USV
			self.serialName = serialName
			self.serialSpeed = serialSpeed
			self.warningCallback = warningCallback
			self.alertCallback = alertCallback
			self.clearAlarmCallback = clearAlarmCallback

			# On essaie de créer l'objet de communication avec les valeurs d'initialisation
			self.__openUSB();

			# Création des variables de contôle de la classe
			self.callbacks = []
			self.messageReceived = None
			self.running = True

			# Démarre l'écoute du port série
			self.__listenUSB()

		# Si on n'y arrive pas, on remonte une exception
		except serial.SerialException as e:
			raise e
