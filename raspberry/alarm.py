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
	# Ce constructeur prend trois paramètres en entrée:
	#		* aType: le type de l'alarme (WARNING ou ALERT)
	#		* aAction: le type d'action ayant déclanché l'alarme
	#		* aMessage: le texte descriptif de l'alarme
	# Le constructeur ajoute une clé unique permettant d'identifier l'alarme
	# ainsi qu'un timestamp afin de situer l'alarme dans le temps
	#
	def __init__(self, aType, aMessage, aAction):

		# Stocke tels quels les deux paramètres passés en entrée
		self.aType = aType
		self.aAction = aAction
		self.aMessage = aMessage

		# Crée un identifiant unique pour cette alarme
		self.aKey = uuid4()

		# Stocke la date et l'heure de l'événement
		self.aTime = strftime('%Y-%m-%d %H:%M:%S')
