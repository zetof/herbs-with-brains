#!/bin/bash 

# $1 contient le nom du Raspberry Pi à contacter
# $2 contient le mot de passe root du Raspberry Pi

tmux new-session -d
tmux send-keys "sshpass -p "$2" ssh -o StrictHostKeyChecking=no root@$1" C-m
tmux send-keys "cd arduino/ard1" C-m
tmux send-keys "vim src/runtime.cpp" C-m
tmux split-window -v
tmux resize-pane -D 15
tmux send-keys "sshpass -p "$2" ssh -o StrictHostKeyChecking=no root@$1" C-m
tmux send-keys "cd /var/log/vertx" C-m
tmux send-keys "tail -n 15 -f system.log" C-m
tmux split-window -h "tty-clock -c"
tmux resize-pane -R 60
tmux select-pane -t 0
tmux split-window -h
tmux send-keys "sshpass -p "$2" ssh -o StrictHostKeyChecking=no root@$1" C-m
tmux send-keys "cd raspberry" C-m
tmux send-keys "vim boot.py" C-m
tmux select-pane -t 0
tmux split-window -v
tmux send-keys "sshpass -p "$2" ssh -o StrictHostKeyChecking=no root@$1" C-m
tmux send-keys "cd arduino/ard2" C-m
tmux send-keys "vim src/runtime.cpp" C-m
tmux select-pane -t 0
tmux new-window "mocp"
tmux select-window -t 0
tmux -2 attach-session
