#!/usr/bin/python
# -*- coding: utf-8 -*-

# Import des librairies
import time
import Adafruit_CharLCD as LCD
import struct
import logging
import logging.config
import AlarmPanel as AP
import USBDaemon as USB

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
ARD1_USB_SPEED = 115200

# Définition du callback lors de la réception d'un message venant d'un Arduino
def processDataFromArduino(receivedData):
	print(receivedData)

# Initialisation du logging
logging.config.fileConfig('logging.conf')
logger = logging.getLogger('vertx')

# Initialisation du panneau des alarmes
alarmPanel = AP.AlarmPanel(WARNING_GPIO, ALERT_GPIO, BUZZER_GPIO, INHIBIT_GPIO, INHIBIT_TIME, BUZZER_ENABLED);

# Initialisation de la communication série avec les Arduinos
arduino1 = USB.USBDaemon(ARD1_USB_PORT, ARD1_USB_SPEED)

# Définition des callbacks lors de la réception des messages provenants des Arduinos
arduino1.subscribe(processDataFromArduino)

lcd = LCD.Adafruit_CharLCD(LCD_RS_GPIO, LCD_EN_GPIO, LCD_D4_GPIO, LCD_D5_GPIO, LCD_D6_GPIO, LCD_D7_GPIO, LCD_NBR_COLS, LCD_NBR_ROWS, LCD_BACK_GPIO)
lcd.clear()
lcd.message('Hello World !!!')
lcd.set_backlight(0)

# On fait tourner le programme un moment
time.sleep(20)
alarmPanel.modifyAlarmState(1, 0)
time.sleep(20)

# On fait le ménage à la sortie de la boucle principale, avant d'aller faire dodo
alarmPanel.stop()
arduino1.stop()
