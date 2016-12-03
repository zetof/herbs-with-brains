#!/bin/bash 
tmux new-session -d
tmux send-keys "cd ~/VERT-X/arduino/ard1" C-m
tmux send-keys "vim src/runtime.ino" C-m
tmux split-window -v
tmux resize-pane -D 15
tmux send-keys "sshpass -p "ktulu666" ssh -o StrictHostKeyChecking=no root@vertx" C-m
tmux send-keys "cd /var/log/vertx" C-m
tmux send-keys "tail -n 15 -f system.log" C-m
tmux split-window -h "tty-clock -c"
tmux resize-pane -R 60
tmux select-pane -t 0
tmux split-window -h
tmux send-keys "sshpass -p "ktulu666" ssh -o StrictHostKeyChecking=no root@vertx" C-m
tmux send-keys "cd python" C-m
tmux send-keys "vim boot.py" C-m
tmux select-pane -t 0
tmux new-window "mocp"
tmux select-window -t 0
tmux -2 attach-session
