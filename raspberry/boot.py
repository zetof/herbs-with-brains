#!/usr/bin/python
# -*- coding: utf-8 -*-

# Import des librairies
import smbus
import time
import Adafruit_CharLCD as LCD
import struct
import logging
import logging.config
import AlarmPannel as AP

# Au démarrage, on suppose que l'incrément du heartbeat est à zéro
myHeartbeat = 0

# Préparation de la communication I2C entre les appareils
i2cBusId = 0x01
i2cAddress1 = 0x03
i2cBus = smbus.SMBus(i2cBusId)

# Initialisation du logging
logging.config.fileConfig('logging.conf')
logger = logging.getLogger('vertx')
# Cette procédure est appelée au démarrage de l'unité. On peut y placer tout
# ce qui nécessite une initialisation comme par exemple:
#   - le logging des erreurs
#   - le démarrage du bus I2C
#		- l'initialisation des varibles globales
#
def startup():
	# La variable sysUp ne sera mis à True que lorsqu'on s'est assuré que tout les
	# compoisants de l'unité ont démarré correctement
	sysUp = False


	# Et tant que ce n'est pas le cas, on boucle...
	while not sysUp:
		try:
			print	i2cReadInteger(i2cBus, i2cAddress1, 0x00)
			print i2cReadFloat(i2cBus, i2cAddress1, 0x20)
			print i2cReadFloat(i2cBus, i2cAddress1, 0x21)
			print i2cReadByte(i2cBus, i2cAddress1, 0x22)
			sysUp = True
		except IOError as error:
			print "Waiting for Arduino to start..."
		time.sleep(1)

def heartbeat():
	global myHeartbeat
	try:
		receivedHeartbeat = bus.read_byte_data(address, 0x01)
		print myHeartbeat 
		myHeartbeat = receivedHeartbeat
	except IOError as error:
		print "Perte de communication avec l'Arduino"

def i2cReadByte(bus, address, command):
	try:
		readByte = bus.read_byte_data(address, command)
		return readByte
	except IOError as error:
		logger.warning('Erreur de lecture d\'un octet pour l\'adresse 0x%0.2x' % address + ' et la commande 0x%0.2x' % command)
		raise

def i2cReadInteger(bus, address, command):
	try:
		block = bus.read_word_data(address, command)
		return block
	except IOError as error:
		logger.warning('Erreur de lecture d\'un entier pour l\'adresse 0x%0.2x' % address + ' et la commande 0x%0.2x' % command)
		raise

def i2cReadFloat(bus, address, command):
	try:
		block = bus.read_i2c_block_data(address, command)
		readFloat = struct.unpack('f', ''.join([chr(i) for i in block[:4]]))[0]
		return round(readFloat, 2)
	except IOError as error:
		logger.warning('Erreur de lecture d\'un réel pour l\'adresse 0x%0.2x' % address + ' et la commande 0x%0.2x' % command)
		raise


# startup()
ap = AP.AlarmPannel(8, 7, 11, 9, 600, True);
lcd = LCD.Adafruit_CharLCD(27, 22, 25, 24, 23, 18, 16, 2, 4)
lcd.clear()
lcd.message('Hello World !!!')
lcd.set_backlight(0)

time.sleep(10)
ap.modifyAlarmState(True, False)
time.sleep(10)
ap.modifyAlarmState(False, True)
time.sleep(10)
ap.modifyAlarmState(True, False)
time.sleep(10)
ap.modifyAlarmState(False, True)
time.sleep(30)
ap.modifyAlarmState(True, False)
time.sleep(20)
ap.stop()
