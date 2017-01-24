#!/usr/bin/python
# -*- coding: utf-8 -*-

import threading
import Adafruit_CharLCD as LCD

# Classe implémentant un écran LCD avancé, se basant sur la bibliothèque de base de Adafruit
#
class LCDDisplay:


	# Liste des constantes
	#
	BACKLIGHT_TIME = 10	# Durée d'allumage de l'écran LCD suite à une action
	BACKLIGHT_CHECK = 1	# Temps d'attente entre deux vérifications de l'allumage du rétro-éclairage du LCD
	BACKLIGHT_ON = 0		# Valeur pour allumer le rétro-éclairage du LCD
	BACKLIGHT_OFF = 1		# Valeur pour éteindre le rétro-éclairage du LCD
	

	# Méthode permettant d'allumer le rétro-éclairage du LCD pour un temps défini
	# par la constante BACKLIGHT_TIMER en secondes
	#
	def __backlightCheck(self):

		# On ne reprogramme le thread de vérification que si le programme principal n'a pas demandé un arrêt général
		if self.running == True:

			# On ne vérifie l'état du rétro-éclairage que si l'allumage global n'est pas enclenché
			if self.backlightAlwaysOn == False:

				# Si un timer est en train de se dérouler, on vérifie son état
				if self.backlightTime > 0:

					# Si le timer est en cours, on lui retire une unité
					# Si il est plus grand que zéro, il est toujours en cours
					# Sinon, on éteint le rétro-éclairage
					self.backlightTime -= 1
					if self.backlightTime == 0:
						self.backlightOff()

			# Finalement, on reboucle pour continuer d'écouter le port USB jusqu'à la fin du programme
			backlightTimer = threading.Timer(self.BACKLIGHT_CHECK, self.__backlightCheck)
			backlightTimer.start()

	# Méthode permettant d'allumer le rétro-éclairage du LCD
	#
	def backlightOn(self):
		self.lcd.set_backlight(self.BACKLIGHT_ON)

	# Méthode permettant d'éteindre le rétro-éclairage du LCD
	#
	def backlightOff(self):
		self.lcd.set_backlight(self.BACKLIGHT_OFF)

	# Méthode permettant de démarrer le rétro-éclairage du LCD pour une période déterminée
	#
	def backlightDelay(self):
		if self.backlightAlwaysOn == False:
			self.backlightTime = self.BACKLIGHT_TIME + 1
			self.backlightOn()

	# Méthode permettant d'allumer en continu le rétro-éclairage du LCD
	#
	def backlightSet(self):
		self.backlightAlwaysOn = True
		self.backlightTime = 0
		self.backlightOn()

	# Méthode permettant d'allumer en continu le rétro-éclairage du LCD
	#
	def backlightReset(self):
		self.backlightAlwaysOn = False
		self.backlightTime = 0
		self.backlightOff()

	# Méthode permettant de vider l'écran
	#
	def clear(self):
		self.lcd.clear()

	# Méthode permettant d'afficher du texte à une position donnée
	#
	def printAt(self, line, column, text):
		self.lcd.set_cursor(column, line)
		self.lcd.message(text)

	# Méthode permettant d'afficher le symbole degrés
	#
	def printDegree(self):
		self.lcd.message('\x00')

	def stop(self):
		self.running = False

	# Constructeur de la classe. Ce constructeur prend en entrée les paramètres suivants:
	#		* rs, en, d4, d5, d6, d7, nbr_cols, nbr_rows, backlight sont les différents
	#				paramètres comme définis par la librairie originale
	#
	def __init__(self, rs, en, d4, d5, d6, d7, nbr_cols, nbr_rows, backlight):

		# Crée l'objet représentant l'écran LCD
		self.lcd = LCD.Adafruit_CharLCD(rs, en, d4, d5, d6, d7, nbr_cols, nbr_rows, backlight)

		# Crée les caractères spéciaux pour le LCD
		self.lcd.create_char(0, [14, 17, 17, 17, 14, 0, 0, 0]) # Degrés
		
		# Création des variables de contôle de la classe
		self.backlightTime = 0
		self.backlightAlwaysOn = False
		self.running = True

		# Démarre la vérification de l'allumage temporaire du rétro-éclairage du LCD
		self.__backlightCheck()
