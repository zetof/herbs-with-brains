#!/usr/bin/python
# -*- coding: utf-8 -*-

import ConfigParser

# Classe permettant de définir le menu affichable via l'écran LCD
#
class Menu:

	# Liste des constantes
	#
	MENU_FILE = 'menu.cfg'
	KEY_SELECT = 600
	KEY_LEFT = 300
	KEY_DOWN = 200
	KEY_UP = 50
	KEY_RIGHT = 0

	# Méthode qui réinitialise le menu
	#
	def resetMenu():
		self.activeLevel = 0
		self.levels = [0, 0, 0]

	# Méthode qui détermine l'élément de menu suivant en fonction de l'action
	# Si on a trouvé un élément de menu suite à l'action du bouton sélectionné, on le renvoie
	# Sinon, on renvoie la valeur None pour indiquer qu'aucune action n'est à mener
	#
	def getAction(self, key):

		# Sauve les valeurs actuelles dans des variables de travail
		activeLevel = self.activeLevel
		level_0 = self.levels[0]
		level_1 = self.levels[1]
		level_2 = self.levels[2]

		# On traite la touche SELECT
		if int(key) == self.KEY_SELECT:
			if activeLevel == 0:
				if 'menu.' + str(level_0) + '.1.label' in self.menu:
					activeLevel = 1
					level_1 = 1
			elif activeLevel == 1:
				if not 'menu.' + str(level_0) + '.' + str(level_1 + 1) + '.label' in self.menu:
					activeLevel = 0
				elif 'menu.' + str(level_0) + '.' + str(level_1) + '.1.label' in self.menu:
					activeLevel = 2
					level_2 = 1
			else:
				if not 'menu.' + str(level_0) + '.' + str(level_1) + '.' + str(level_2 + 1) + '.label' in self.menu:
					activeLevel = 1

		# On traite la touche DOWN
		elif int(key) == self.KEY_DOWN:
			if activeLevel == 0:
				if 'menu.' + str(level_0 + 1) + '.label' in self.menu:
					level_0 += 1
			elif activeLevel == 1:
				if 'menu.' + str(level_0) + '.' + str(level_1 + 1) + '.label' in self.menu:
					level_1 += 1
			else:
				if 'menu.' + str(level_0) + '.' + str(level_1) + '.' + str(level_2 + 1) + '.label' in self.menu:
					level_2 += 1

		# On traite le touche UP
		elif int(key) == self.KEY_UP:
			if activeLevel == 0:
				if 'menu.' + str(level_0 - 1) + '.label' in self.menu:
					level_0 -= 1
			elif activeLevel == 1:
				if 'menu.' + str(level_0) + '.' + str(level_1 - 1) + '.label' in self.menu:
					level_1 -= 1
			else:
				if 'menu.' + str(level_0) + '.' + str(level_1) + '.' + str(level_2 - 1) + '.label' in self.menu:
					level_2 -= 1

		# Si il y a eu un changement, on sauve les variables de travail dans les propriétés de la classe
		if activeLevel != self.activeLevel or level_0 != self.levels[0] or level_1 != self.levels[1]:
			self.activeLevel = activeLevel
			self.levels[0] = level_0
			self.levels[1] = level_1
			self.levels[2] = level_2

			# Et on renvoie la valeur du menu par rapport au niveau où on se trouve
			if activeLevel == 0:
				return self.menu['menu.' + str(level_0) + '.label']
			elif activeLevel == 1:
				return self.menu['menu.' + str(level_0) + '.' + str(level_1) + '.label']
			else:
				return self.menu['menu.' + str(level_0) + '.' + str(level_1) + '.' + str(level_2) + '.label']

		# Si pas de changement, on renvoie None pour le signifier
		else:
			return None

	# Constructeur de la classe
	#
	def __init__(self):

		# On lit le fichier de configuration du menu et on l'assigne à un dictionnaire
		configFile = ConfigParser.ConfigParser()
		configFile.read([self.MENU_FILE])
		self.menu = dict(configFile.items('menu'))

		# A la base, on travaille sur le menu de niveau le plus haut et on est positionné sur le premier élément
		self.activeLevel = 0
		self.levels = [0, 0, 0]
