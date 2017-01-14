#!/bin/bash 

# $1 contient le nom du Raspberry Pi à contacter
# $2 contient le mot de passe root du Raspberry Pi

sshpass -p "$2" scp root@$1:/root/.vimrc ../config/
sshpass -p "$2" scp root@$1:/root/arduino/ard1/platformio.ini ../arduino/ard1/
sshpass -p "$2" scp -r root@$1:/root/arduino/ard1/src ../arduino/ard1/
sshpass -p "$2" scp -r root@$1:/root/arduino/ard1/lib ../arduino/ard1/
sshpass -p "$2" scp root@$1:/root/raspberry/\{boot.py,AlarmPanel.py,USBDaemon.py,logging.conf\} ../raspberry/
