#!/bin/bash 

# $1 contient le nom du Raspberry Pi à contacter
# $2 contient le mot de passe root du Raspberry Pi

sshpass -p "$2" scp ../arduino/ard1/platformio.ini root@$1:/root/arduino/ard1
sshpass -p "$2" scp -r ../arduino/ard1/lib root@$1:/root/arduino/ard1
sshpass -p "$2" scp -r ../arduino/ard1/src root@$1:/root/arduino/ard1
sshpass -p "$2" scp ../config/.vimrc root@$1:/root
sshpass -p "$2" scp -r ../raspberry root@$1:/root/raspberry
