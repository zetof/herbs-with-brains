#!/usr/bin/python
# -*- coding: utf-8 -*-

import ConfigParser

# Classe permettant de définir une alarme
# Cette alarme est utilisée afin de stocker un événement de type WARNING ou ALERT
#
class I18N:

	# Liste des constantes
	#
	BASE_DIR = 'i18n/'

	# Méthode effectuant la translation d'un label dans la langue sélectionnée
	#
	def t(self, label, data):

		# On considère que la traduction n'a pas encore été faite
		translated = '<I18N:' +self.locale + ':' + label + '>'

		# Construit la phrase finale à partir de la traduction et des valeurs passées
		# Si on ne trouve pas de traduction pour le label, on l'émet tel quel
		if label in self.i18n:
			translated = self.i18n[label] % tuple(data)
		return translated

	# Constructeur de la classe
	# Ce constructeur prend deux paramètres en entrée:
	#		* locale: la locale utilisée dans le programme
	#		* languageFile: le fichier contenant les traductions pour la locale
	#
	def __init__(self, locale, languageFile):

		# Sauve la locale
		self.locale = locale

		# Prépare le parser, lit le fichier et stocke les traductions dans une structure
		configFile = ConfigParser.ConfigParser()
		configFile.read([self.BASE_DIR + locale + '/' + languageFile])
		self.i18n = dict(configFile.items(locale))
