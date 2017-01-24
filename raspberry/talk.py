#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
import logging.config
import time
import serial
from alarms import Alarms
from lcd import LCDDisplay
from alarmpanel import AlarmPanel
from usb import USBDaemon

# Classe permettant de piloter tout type de communication dans l'unité VERT-X à savoir:
#		* Le panneau des alarmes lumineuses et visuelles
#		* L'écran LCD de l'unité
#		* L'écriture dans les logs applicatifs
#		* La communication avec les Arduinos
#
class Talk:

	# Liste des états hérités de la classe de logging
	#
	DEBUG = logging.DEBUG				# Message de type DEBUG
	INFO = logging.INFO					#	Message de type INFO
	WARNING = logging.WARNING		# Message de type WARNING
	ERROR = logging.ERROR				# Message de type ERROR
	CRITICAL = logging.CRITICAL	# Message de type CRITICAL

	# Paramètres de connexion à l'ARDUINO en cas de problème
	CONNECT_MAX_TRIALS = 3	# Nombre de tentatives de connection à un Arduino avant la levée d'une alarme
	CONNECT_WAIT_TIME = 10	# Temps d'attente entre deux essais de connexion

	# Méthode permettant de logger un message dans les fichiers de log
	#
	def log(self, mType, message):

		# Log au niveau requis
		if mType == logging.DEBUG:
			self.logger.debug(message)
		elif mType == self.INFO:
			self.logger.info(message)
		elif mType == self.WARNING:
			self.logger.warning(message)
		elif mType == self.ERROR:
			self.logger.error(message)
		elif mType == self.CRITICAL:
			self.logger.critical(message)

	# Méthode permettant l'ajout d'une alarme dans la liste des alarmes
	#
	def setAlarm(self, aType, aMessage, onPanel, aKey = None):

		# Dans tous les cas, si le message passé n'est pas égal à False, on enregistre le message dans les logs
		if aMessage != False:
			self.log(aType, aMessage)

		# Si on doit afficher l'alarme sur le panneau des alarmes, on ajoute une alarme dans la liste
		# et on envoie une demande de notification au panneau des alarmes
		if onPanel == True:
			if aType == self.WARNING:
				self.alarmPanel.setWarning()
			elif aType == self.ERROR or aType == self.CRITICAL:
				self.alarmPanel.setAlert()
			aKey = self.alarms.addAlarm(aType, aMessage, aKey) 

		# On retourne la référence de l'alarme enregistrée
		return aKey

	# Méthode permettant la suppression d'une alarme dans la liste des alarmes
	# La suppression se fait par la clé précédemment enregistrée
	# A la suppression, on vérifie si on doit mettre à jour les flags d'alarme dans le panneau des alarmes
	#
	def resetAlarm(self, aKey, aMessage):

		# Si le message est différent de False on l'enregistre dans les logs sous forme d'une INFO
		if aMessage != False:
			self.log(self.INFO, aMessage)

		# On supprime l'alarme de la liste des alarmes et on récupère son type
		aType = self.alarms.clearAlarm(aKey)

		# Suivant le type de l'alarme supprimée, on vérifie si le panneau des alarmes est à jour
		if aType == self.WARNING:
			if not self.alarms.anyWarning():
				self.alarmPanel.resetWarning()
		elif aType == self.ERROR or self.CRITICAL:
			if not self.alarms.anyAlert():
				self.alarmPanel.resetAlert()

	# Méthode ajoutant un Arduino dans la liste des Arduinos à contacter
	#
	def addArduino(self, aName, aPort, aSpeed, callback):
		
		# On initialise les paramètres de connexion
		alarm = None
		arduino = None
		nbrOfTrials = 0

		# Tant qu'on n'a pas réussi une connection vers l'Arduino, on réessaie
		while arduino == None:

			# On tente une connection vers l'Arduino
			try:
				arduino = USBDaemon(aName, aPort, aSpeed, callback)
				self.arduinos.append(arduino)

				# A ce stade, la connexion est réussie
				# Si nous avions une erreur de connexion auparavent, on la supprime
				if alarm != None:
					self.resetAlarm(alarm, 'Redémarrage OK')

			# Si on y arrive pas, on rapporte l'erreur et on boucle
			except serial.SerialException as e:
				
				# On incrémente le nombre d'essais infructueux à la connexion
				# Si on a dépassé le nombre maximum d'essais, on continue d'essayer mais on envoie une ALARM
				nbrOfTrials += 1
				if nbrOfTrials == self.CONNECT_MAX_TRIALS:
					alarm = self.setAlarm(self.ERROR, 'Impossible de se connecter à l\'Arduino: ' + aName, True)

				# On attend un instant avant de retenter
				time.sleep(self.CONNECT_WAIT_TIME)

	# Méthode à appeler à l'arrêt général du programme afin de quitter tous les processus de façon contrôlée
	#
	def stop(self):

		# On arrête les processus tournant sur le panneau des alarmes, l'écran LCD et tous les Arduinos
		self.alarmPanel.stop()
		self.lcd.stop()
		for arduino in self.arduinos:
			arduino.stop()

	# Constructeur de la classe
	#
	def __init__(self, loggerName):

		# Initialisation du logging
		logging.config.fileConfig('logging.conf')
		self.logger = logging.getLogger(loggerName)

		# Liste des alarmes en cours
		self.alarms = Alarms()

		# Initialisation du panneau des alarmes
		self.alarmPanel = AlarmPanel(8, 7, 11, 9, 600, True);

		# Initialisation de l'écran LCD
		self.lcd = LCDDisplay(27, 22, 25, 24, 23, 18, 16, 2, 4)

		# Liste des Arduinos à contacter
		self.arduinos = []
