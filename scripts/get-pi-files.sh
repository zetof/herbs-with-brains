#!/bin/bash 
sshpass -p 'ktulu666' scp root@vertx:/root/.vimrc ../config/
sshpass -p 'ktulu666' scp root@vertx:/root/arduino/ard1/platformio.ini ../arduino/ard1/
sshpass -p 'ktulu666' scp -r root@vertx:/root/arduino/ard1/src ../arduino/ard1/
sshpass -p 'ktulu666' scp -r root@vertx:/root/arduino/ard1/lib ../arduino/ard1/
sshpass -p 'ktulu666' scp root@vertx:/root/python/\{boot.py,AlarmPanel.py,USBDaemon.py,logging.conf\} ../raspberry/
