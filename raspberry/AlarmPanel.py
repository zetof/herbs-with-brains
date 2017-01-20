#!/usr/bin/python
# -*- coding: utf-8 -*-

import RPi.GPIO as GPIO
import threading
import time
import uuid

# Classe permettant de définir une alarme. Cette alarme est utilisée afin de stocker un événement de type WARNING ou ALERT
#
class Alarm:

	# Liste des constantes
	#
	WARNING = 'W'	# Valeur d'une alarme de type WARNING
	ALERT = 'A'		# Valeur d'une alarme de type ALERT

	# Constructeur de la classe
	#
	def __init__(self, aType, aMessage):

		# Stocke tels quels les deux paramètres passés en entrée
		self.aType = aType
		self.aMessage = aMessage

		# Stocke un identifiant unique pour cette alarme
		self.aKey = uuid.uuid4()

		# Stocke la date et l'heure de l'événement
		self.aTime = time.strftime("%Y-%m-%d %H:%M:%S")

# Classe permettant de stocker tous les WARNING et toutes les ALERT en cours
#
class AlarmArray:

	# Méthode permettant d'ajouter un alarme de type WARNING à la liste des alarmes
	#
	def addWarning(self, aMessage):

		# Préparation de l'alarme et ajout à la liste
		alarm = Alarm(Alarm.WARNING, aMessage)
		self.alarmArray.append(alarm)

		# On renvoie à l'appelant la clé sauvegardée dans la list
		return alarm.aKey

	# Méthode permettant d'ajouter un alarme de type ALERT à la liste des alarmes
	#
	def addAlert(self, aMessage):

		# Préparation de l'alarme et ajout à la liste
		alarm = Alarm(Alarm.ALERT, aMessage)
		self.alarmArray.append(alarm)

		# On renvoie à l'appelant la clé sauvegardée dans la list
		return alarm.aKey

	# Méthode permettant de supprimer une entrée dans la liste des alarmes
	#
	def clearAlarm(self, aKey):
		for index, alarm in enumerate(self.alarmArray):
			if alarm.aKey == aKey:
				del self.alarmArray[index]
				break

	# Méthode permettant de vérifier si au moins une alarme de type WARNING est présente dans la liste
	#
	def anyWarning(self):
		if sum(alarm.aType == Alarm.WARNING for alarm in self.alarmArray) > 0:
			return True
		else:
			return False

	# Méthode permettant de vérifier si au moins une alarme de type ALERT est présente dans la liste
	#
	def anyAlert(self):
		if sum(alarm.aType == Alarm.ALERT for alarm in self.alarmArray) > 0:
			return True
		else:
			return False

	# Constructeur de la classe
	#
	def __init__(self):

		# Définition des propriétés de la classe
		self.alarmArray = []

# Classe permettant de piloter le panneau des alarmes de l'unité VERT-X
# Ce panneau comprend:
#		* Une LED OK (verte)
#		* Une LED de WARNING (jaune)
#		* Une LED d'ALERT (rouge)
#		* Un buzzer permettant d'émettre des alarmes sonores
#		* Un bouton permettant de couper temporairement le buzzer
#
class AlarmPanel:

	# Liste des constantes
	#
	ASTABLE_HIGH_TIME = 0.2	# Durée d'un bip sonore correspondant au signal de WARNING exprimé en secondes
	ASTABLE_LOW_TIME = 5		# Délai entre deux bips sonores d'un signal de WARNING exprimé en secondes
	INHIBIT_TIME = 600			# Temps d'action du bouton INHIBIT coupant l'alarme sonore exprimé en secondes

	# Méthode de callback appelée chaque seconde pendant la période d'inhibition du buzzer
	# Décrémente le délai et vérifie si on est arrivé à la fin de l'inhibition ou pas
	# Permet une fin du thread harmonieuse en cas de fermeture du programme
	#
	def __inhibitRunning(self):

		# On ne relance le timer que si le programme principal n'a pas demandé une fin d'exécution par la méthode stop()
		if self.running == True:

			# On soustrait une seconde et si on n'est pas à la fin du timer, on reprogramme une exécution
			self.inhibitRemaining -= 1
			if self.inhibitRemaining != 0:
				inhibitTimer = threading.Timer(1, self.__inhibitRunning)
				inhibitTimer.start()

			# Fin de l'inhibition, si il y a une alerte, on relance immédiatement le buzzer
			else:
				if self.alert == True:
					GPIO.output(self.buzzer, 1)

	# Méthode de callback lorsque le bouton inhibit a été pressé
	#
	def __inhibitPressed(self, channel):

		# On ne fait qu'une seule inhibation à la fois
		# Si une période d'inhibation est en cours, on ne fait rien
		if self.inhibitRemaining == 0:

			# On force l'arrête du buzzer et on démarre le timer pour la période définie
			#
			GPIO.output(self.buzzer, 0)
			self.inhibitRemaining = self.INHIBIT_TIME + 1
			self.__inhibitRunning()

	# Méthode qui tourne constamment en thread, lancée par le constructeur
	# Immite le fonctionnement d'un astable, avec un cycle haut et un cycle bas
	# Cet astable reste en position haute pendant x secondes (défini par la valeur de la constante ASTABLE_HIGH_TIME)
	# Et en position basse pendant y secondes (défini par la valeur de la constante ASTABLE_LOW_TIME)
	#
	def __buzzerAstable(self, state):

		# On part du principe qu'à la base, aucun bip ne doit être émis
		highValue = 0
		lowValue = 0

		# On n'émet aucun bip si la fonction est désactivée globalement à la création du panneau des alarmes
		# ou si le bouton d'inhibition de l'alarme sonore a été poussé
		if self.buzzerEnabled == True:
			if self.inhibitRemaining == 0:

				# Si un bip peut être émis, on vérifie si on est en présence d'une alarme de type WARNING ou ALERT
				# Dans les deux cas, le front haut doit générer un bip
				# Si c'est un WARNING, on coupe le front bas, sinon, pour une ALERT, le son doit être continu donc
				# également haut pour la partie normalement basse de l'astable
				if self.alarmList.anyWarning() == True or self.alarmList.anyAlert() == True:
					highValue = 1
				if self.alarmList.anyAlert() == True:
					lowValue = 1

		# Génération proprement dite du son si nécessaire et reprogrammation du front suivant
		# A noter que l'on ne reprogramme un front que si le panneau est censé fonctionner
		# Si on a utilisé la métode stop(), il n'y a plus de signal ce qui permet de terminer
		# la classe de façon fluide
		if self.running == True:
			if state == True:
				GPIO.output(self.buzzer, highValue)
				astableTimer = threading.Timer(self.ASTABLE_HIGH_TIME, self.__buzzerAstable, [False])
				astableTimer.start()
			else:
				GPIO.output(self.buzzer, lowValue)
				astableTimer = threading.Timer(self.ASTABLE_LOW_TIME, self.__buzzerAstable, [True])
				astableTimer.start()


	# Méthode permettant d'arrêter de façon propre la classe par arrêt programmé des threads
	# On en profite pour remettre à zéro les alarmes
	#
	def stop(self):
		GPIO.output(self.warningLED, 0);
		GPIO.output(self.alertLED, 0);
		GPIO.output(self.buzzer, 0);
		self.running = False

	# Méthode permettant d'activer l'alarme sonore de façon permanente
	#
	def activateBuzzer(self):
		self.buzzerEnabled = True

	# Méthode permettant de désactiver l'alarme sonore de façon permanente
	#
	def deactivateBuzzer(self):
		self.buzzerEnabled = False

	# Méthode permettant la génération d'une alarme de type WARNING
	#
	def addWarning(self, message):

		# Gestion de l'état des LEDs
		GPIO.output(self.warningLED, 1)

		# On ajoute une WARNING à la liste des alarmes et on retourne sa clé
		return self.alarmList.addWarning(message)

	# Méthode permettant la génération d'une alarme de type ALERT
	#
	def addAlert(self, message):

		# Gestion de l'état des LEDs
		GPIO.output(self.alertLED, 1)

		# On ajoute une ALERT à la liste des alarmes et on retourne sa clé
		return self.alarmList.addAlert(message)

	# Méthode permettant la suppression d'une alarme
	#
	def clearAlarm(self, key):

		# On retire l'alarme de la list, basée sur la clé passée
		self.alarmList.clearAlarm(key)

		# On rectifie l'état des LEDs si nécessaire
		if self.alarmList.anyWarning() == False:
			GPIO.output(self.warningLED, 0)
		if self.alarmList.anyAlert() == False:
			GPIO.output(self.alertLED, 0)


	# Constructeur de la classe. Ce constructeur prend en entrée les paramètres suivants:
	#		* warningLED: le numéro du GPIO destiné à piloter la LED des WARNINGs
	#		* alertLED: le numéro du GPIO destiné à piloter la LED des ALERTs
	#		* buzzer: le numéro du GPIO destiné à piloter le BUZZER
	#		* inihibitButton: le numéro du GPIO destiné à recevoir les actions venant du bouton INHIBIT
	#		* inihibitTime: le temps en secondes pendant lequel l'alarme sonore est coupée suit à une pression du bouton INHIBIT
	#		* buzzerEnabled: si mis à False, aucune alarme sonore n'est générée par le système
	#		A noter qu'on ne pilote pas la LED verte. Si il n'y a pas d'alarme, celle-ci brille de façon automatique
	#
	def __init__(self, warningLED, alertLED, buzzer, inhibitButton, inhibitTime, buzzerEnabled):

		# Sauvegarde les valeurs d'initialisation pour réutilisation
		self.warningLED = warningLED
		self.alertLED = alertLED
		self.buzzer = buzzer
		self.inhibitButton = inhibitButton
		self.inhibitTime = inhibitTime
		self.buzzerEnabled = buzzerEnabled

		# Création des variables de contôle de la classe
		self.warning = False
		self.alert = False
		self.inhibitRemaining = 0
		self.running = True
		self.alarmList = AlarmArray()

		# Référence les GPIOs par leur numéro réel, pas par le numéro de pin
		GPIO.setmode(GPIO.BCM)

		# Prépare les GPIOs en sortie suivant ce qui a été défini par le constructeur
		# Par défaut, pas d'alarmes, pas de buzzer
		GPIO.setup(warningLED, GPIO.OUT)
		GPIO.setup(alertLED, GPIO.OUT)
		GPIO.setup(buzzer, GPIO.OUT)
		GPIO.output(warningLED, 0);
		GPIO.output(alertLED, 0);
		GPIO.output(buzzer, 0);

		# Définit les paramètres du bouton d'inhibition, par défaut, le GPIO est sur une valeur haute
		# Le bouton crée un front descendant qui appelle la méthode de callback __inhibit_pressed pour traitement
		GPIO.setup(inhibitButton, GPIO.IN, pull_up_down=GPIO.PUD_UP)
		GPIO.add_event_detect(9, GPIO.FALLING, callback=self.__inhibitPressed, bouncetime=300)

		# Démarre la génération du signal sonore de warning pour le buzzer
		self.__buzzerAstable(True)
