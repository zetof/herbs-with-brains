#!/usr/bin/python
# -*- coding: utf-8 -*-

from time import strftime
from uuid import uuid4
import logging

# Classe permettant de définir une alarme
# Cette alarme est utilisée afin de stocker un événement de type WARNING ou ALERT
#
class Alarm:

	# Liste des constantes
	#
	WARNING = logging.WARNING	# Valeur d'une alarme de type WARNING
	ALERT = logging.ERROR				# Valeur d'une alarme de type ALERT

	# Constructeur de la classe
	# Ce constructeur prend deux paramètres en entrée:
	#		* aType: le type de l'alarme (WARNING ou ALERT)
	#		* aMessage: le texte descriptif de l'alarme
	# Le constructeur ajoute une clé unique permettant d'identifier l'alarme
	# ainsi qu'un timestamp afin de situer l'alarme dans le temps
	#
	def __init__(self, aType, aMessage, aKey):

		# Stocke tels quels les deux paramètres passés en entrée
		self.aType = aType
		self.aMessage = aMessage

		# Crée un identifiant unique pour cette alarme si on n'en a pas reçu
		# Sinon, on stocke l'identifiant reçu
		if aKey != None:
			self.aKey = aKey
		else:
			self.aKey = uuid4()
		print self.aKey
		# Stocke la date et l'heure de l'événement
		self.aTime = strftime("%Y-%m-%d %H:%M:%S")
