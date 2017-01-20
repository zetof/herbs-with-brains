#!/r/bin/python
# -*- coding: utf-8 -*-

# Import des librairies
import time
import struct
import serial
import logging
import logging.config
import AlarmPanel as AP
import USBDaemon as USB
import LCDDisplay as LCD

# Définition des propriétés du panneau des alarmes
WARNING_GPIO = 8
ALERT_GPIO = 7
BUZZER_GPIO = 11
INHIBIT_GPIO = 9
INHIBIT_TIME = 600
BUZZER_ENABLED = True

# Définition des propriétés de l'écran LCD
LCD_RS_GPIO = 27
LCD_EN_GPIO = 22
LCD_D4_GPIO = 25
LCD_D5_GPIO = 24
LCD_D6_GPIO = 23
LCD_D7_GPIO = 18
LCD_BACK_GPIO = 4
LCD_NBR_ROWS = 2
LCD_NBR_COLS = 16

# Définition des propriétés de communication série avec les Arduinos
ARD1_USB_PORT = '/dev/ard1'
ARD2_USB_PORT = '/dev/ttyUSB0'
ARD_USB_SPEED = 115200

# Initialisation du logging
logging.config.fileConfig('logging.conf')
logger = logging.getLogger('vertx')

# Initialisation du panneau des alarmes
alarmPanel = AP.AlarmPanel(WARNING_GPIO, ALERT_GPIO, BUZZER_GPIO, INHIBIT_GPIO, INHIBIT_TIME, BUZZER_ENABLED);

# Fonction permettant le traitement d'une alerte de type WARNING
# Cette fonction peut être utilisée en callback des différentes classes utilisées par le programme
#
def warning(alarmMessage, notifyPanel, notifyInternet):
	warningKey = None
	logger.warning(alarmMessage)
	if notifyPanel == True:
		warningKey = alarmPanel.addWarning(alarmMessage)
	if warningKey != None:
		return warningKey

# Fonction permettant le traitement d'une alerte de type ALERT
# Cette fonction peut être utilisée en callback des différentes classes utilisées par le programme
#
def alert(alarmMessage, notifyPanel, notifyInternet):
	alertKey = None
	logger.error(alarmMessage)
	if notifyPanel == True:
		alertKey =  alarmPanel.addAlert(alarmMessage)
	if alertKey != None:
		return alertKey

# Fonction permettant la suppression d'une alarme par sa clé d'enregistrement
# Cette fonction peut être utilisée en callback des différentes classes utilisées par le programme
#
def clearAlarm(alarmKey, alarmMessage):
	if alarmMessage != False:
		logger.info(alarmMessage)
	alarmPanel.clearAlarm(alarmKey)

# Définition du callback lors de la réception d'un message venant d'un Arduino
# Définition du callback lors de la réception d'un message venant d'un Arduino
def processDataFromArduino(receivedData):
	print(receivedData)
	lcd.clear()
	lcd.printAt(0, 0, receivedData)
	lcd.backlightDelay()

# Tant que toutes les connxions n'ont pas été faites, on boucle
arduino1 = None
while arduino1 == None:

	# On essaie d'établir les liens de communication série vers les Arduinos
	try:
		# Initialisation de la communication série avec les Arduinos
		arduino1 = USB.USBDaemon(ARD1_USB_PORT, ARD_USB_SPEED, warning, alert, clearAlarm)
		arduino2 = USB.USBDaemon(ARD2_USB_PORT, ARD_USB_SPEED, warning, alert, clearAlarm)

		# Définition des callbacks lors de la réception des messages provenants des Arduinos
		arduino1.subscribe(processDataFromArduino)
		arduino2.subscribe(processDataFromArduino)

	# Si on y arrive pas, on rapporte l'erreur et on boucle
	except serial.SerialException as e:
		logger.error('Problème à l\'ouverture du port USB avec Arduino 1: ')
		time.sleep(10)

# Initialisation de l'écran LCD
lcd = LCD.LCDDisplay(LCD_RS_GPIO, LCD_EN_GPIO, LCD_D4_GPIO, LCD_D5_GPIO, LCD_D6_GPIO, LCD_D7_GPIO, LCD_NBR_COLS, LCD_NBR_ROWS, LCD_BACK_GPIO)
lcd.backlightOff()

# On fait tourner le programme un moment
time.sleep(60)

# On fait le ménage à la sortie de la boucle principale, avant d'aller faire dodo
alarmPanel.stop()
arduino1.stop()
arduino2.stop()
lcd.stop()
