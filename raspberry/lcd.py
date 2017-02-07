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

	# Méthode permettant l'affichage de caractères spéciaux à partir de tags spécifiques
	# Les caractères spéciaux sont définis dans le constructeur par la commande "create_char"
	#
	def __replaceCustomChars(self, text):
		text = text.replace('{degree}', '\x00')
		text = text.replace('{up}', '\x01')
		text = text.replace('{both}', '\x02')
		text = text.replace('{down}', '\x03')
		text = text.replace('{select}', '\x04')
		return text

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

	# Méthode permettant de savoir si le rétro-éclairage est allumé
	#
	def isBacklightOn(self):
		if self.backlightAlwaysOn == True or self.backlightTime > 0:
			return True
		else:
			return False

	# Méthode permettant d'afficher du texte sur les deux lignes suivant un format spécial
	#
	def printMessage(self, text):

		# On remplace tous les tags spéciaux par leur code tel que défini dans le constructeur
		text = self.__replaceCustomChars(text)

		# Le séparateur des deux lignes est le pipe (|)
		splitText = text.split('|')

		# On efface l'écran ce qui positionne automatiquement le curseur en (0, 0)
		self.lcd.clear()

		# On affiche la première ligne
		self.lcd.message(splitText[0])

		# Et on affiche la deuxième ligne si elle existe
		if len(splitText) > 1:
			self.lcd.set_cursor(0, 1)
			self.lcd.message(splitText[1].replace('{degree}', '\x00'))

		# Finallement, on allume le rétro-éclairage pour la durée définie
		self.backlightDelay()

	# Méthode permettant d'afficher le symbole degrés
	#
	def printDegree(self):
		self.lcd.message('\x00')

	# Permet de terminer proprement le processus de rétro-éclairage
	#
	def stop(self):
		self.running = False

	# Constructeur de la classe. Ce constructeur prend en entrée les paramètres suivants:
	#		* rs, en, d4, d5, d6, d7, nbr_cols, nbr_rows, backlight sont les différents	paramètres définis par la librairie originale
	#
	def __init__(self, rs, en, d4, d5, d6, d7, nbr_cols, nbr_rows, backlight):

		# Crée l'objet représentant l'écran LCD
		self.lcd = LCD.Adafruit_CharLCD(rs, en, d4, d5, d6, d7, nbr_cols, nbr_rows, backlight)

		# Crée les caractères spéciaux pour le LCD
		self.lcd.create_char(0, [14, 17, 17, 14, 0, 0, 0, 0])	# Degrés
		self.lcd.create_char(1, [4, 14, 31, 4, 4, 4, 4, 4]) 		# Flèche vers le haut
		self.lcd.create_char(2, [4, 14, 31, 4, 4, 31, 14, 4]) 	# Flèche bidirectionnelle
		self.lcd.create_char(3, [4, 4, 4, 4, 4, 31, 14, 4]) 		# Flèche vers le bas
		self.lcd.create_char(4, [0, 1, 5, 13, 31, 12, 4, 0]) 		# Select
		
		# Création des variables de contôle de la classe
		self.backlightTime = 0
		self.backlightAlwaysOn = False
		self.running = True

		# Démarre la vérification de l'allumage temporaire du rétro-éclairage du LCD
		self.__backlightCheck()
