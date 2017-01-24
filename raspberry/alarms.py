#!/usr/bin/python
# -*- coding: utf-8 -*-

from alarm import Alarm

# Classe permettant de stocker dans une liste tous les WARNING et toutes les ALERT en cours
#
class Alarms:

	# Méthode permettant d'ajouter une alarme de façon générale
	#
	def addAlarm(self, aType, aMessage, aKey):

		# Si on a reçu un identifiant, on vérifie qu'il n'existe pas encore dans la liste
		# Si il existe, on supprime l'existant et on le remplace par l'événement le plus récent
		if aKey != None:
			for index, alarm in enumerate(self.alarms):
				if alarm.aKey == aKey:
					del self.alarms[index]
					break

		# Préparation de l'alarme et ajout à la liste
		alarm = Alarm(aType, aMessage, aKey)
		self.alarms.append(alarm)

		# On renvoie à l'appelant la clé sauvegardée dans la list
		return alarm.aKey
	
	# Méthode permettant de supprimer une entrée dans la liste des alarmes
	# La méthode retourne le type de l'alarme précédemment enregistrée (WARNING ou ALERT)
	#
	def clearAlarm(self, aKey):
		aType = None
		for index, alarm in enumerate(self.alarms):
			if alarm.aKey == aKey:
				aType = alarm.aType
				del self.alarms[index]
				break
		return aType

	# Méthode permettant de vérifier si au moins une alarme de type WARNING est présente dans la liste
	#
	def anyWarning(self):
		if sum(alarm.aType == Alarm.WARNING for alarm in self.alarms) > 0:
			return True
		else:
			return False

	# Méthode permettant de vérifier si au moins une alarme de type ALERT est présente dans la liste
	#
	def anyAlert(self):
		if sum(alarm.aType == Alarm.ALERT for alarm in self.alarms) > 0:
			return True
		else:
			return False

	# Constructeur de la classe
	#
	def __init__(self):

		# Définition des propriétés de la classe
		self.alarms = []
