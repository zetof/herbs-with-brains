#!/usr/bin/python
# -*- coding: utf-8 -*-

from alarm import Alarm

# Classe permettant de stocker dans une liste tous les WARNING et toutes les ALERT en cours
#
class Alarms:

	# Méthode permettant d'ajouter une alarme de façon générale
	#
	def addAlarm(self, aType, aAction, aMessage):

		# Préparation de l'alarme et ajout à la liste
		alarm = Alarm(aType, aAction, aMessage)
		self.alarms.append(alarm)

		# On renvoie à l'appelant la clé sauvegardée dans la list
		return alarm.aKey
	
	# Méthode permettant de supprimer une entrée dans la liste des alarmes sur base de sa clé
	# La méthode retourne le type de l'alarme précédemment enregistrée (WARNING ou ALERT)
	#
	def clearAlarmFromKey(self, aKey):
		for index, alarm in enumerate(self.alarms):
			if alarm.aKey == aKey:
				aType = alarm.aType
				del self.alarms[index]
				break

	# Méthode permettant de supprimer toutes les entrées dans la liste des alarmes sur base d'un type d'action
	# On peut éventuellement entrer le type d'alarme à supprimer, par défaut tous les types sont supprimés
	#
	def clearAlarmFromAction(self, aAction):
		for index, alarm in enumerate(self.alarms):
			if alarm.aAction == aAction:
				aType = alarm.aType
				del self.alarms[index]

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
