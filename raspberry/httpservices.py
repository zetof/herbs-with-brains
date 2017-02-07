#!/usr/bin/python
# -*- coding: utf-8 -*-

import requests
import web
from threading import Thread
import json
from requests.auth import HTTPBasicAuth

# Classe permettant de communiquer avec internet
# Cette classe permet d'envoyer des requêtes sur internet au travers de la librairie requests
# Elle permet également de recevoir des commandes d'internet grâce à la librairie web.py
# La librairie json permet d'encoder et de décoder des requêtes json
#
class HttpServices:

	# Méthode permettant d'envoyer un message à la plate-forme VERT-X CONNECT
	#
	def sendRequest(self, service, message):
		url = self.baseURL + '/' + service
		r = requests.put(url, auth=HTTPBasicAuth('vertx', 'LeVertCaGere'))
		print r.status_code
		print r.text

	# Constructeur de la classe
	# Ce constructeur prend quatre paramètres en entrée:
	#		* baseURL: l'url de base utilisée pour contacter la plate-forme VERT-X CONNECT
	#		* user: l'utilisateur défini pour l'utilisation des services web
	#		* password: le mot de passe défini pour l'utilisation des services web
	#		* callback: la fonction utilisée dans le programme principal pour traiter les commandes venant d'internet
	#
	def __init__(self, baseURL, user, password, callback):

		# Stocke tel quel le paramètre passé en entrée
		self.baseURL = baseURL

		# Démarre l'écoute des commandes venant d'internet
		# On démarre le serveur en mode DAEMON afin qu'il se coupe à la sortie du programme principal
		httpDaemon = HttpCommands(callback)
		httpDaemon.daemon = True
		httpDaemon.start()

# Classe permettant de démarer le serveur qui écoute les commandes en provenance d'internet
# Cette classe accepte un paramètre en entrée qui définit la fonction à rappeler pour le traitement d'une commande
#
class HttpCommands(Thread):

	# Le constructeur permet de sauver le callback
	#
	def __init__(self, callback):
		Thread.__init__(self)
		self.callback = callback

	# Méthode lancée au démarrage du serveur de commandes en mode DAEMON
	#
	def run(self):

		# Liste des urls exposés à internet par la plate-forme VERT-X et leur classes associées
		urls = ('/', 'ProcessJSON')

		# Démarrage de l'écoute pour la réception des commandes et sauvegarde du callback dans le contexte web
		webApp = web.application(urls, globals())
		web.callback = self.callback
		webApp.run()

# Classe appelée pour le traitement des commandes au format JSON
#
class ProcessJSON:

	# Pour les méthodes de type GET, cette méthode est déroulée
	#
	def GET(self):

		# Récupère les paramètres dans le requête
		formData = web.input(command = None)

		# Appelle le traitement de la demande
		if formData.command != None:
			web.callback('La commande passée est: %s %s' % (formData.command.encode('utf-8'), formData.r.encode('utf-8')))
		else:
			web.callback('LO from the INTERNET!')
		return 'coucou !'
