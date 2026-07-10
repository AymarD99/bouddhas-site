#!/usr/bin/env bash
# MiMo serve watchdog: relance mimo serve sur 4097 si down
# Miroir de opencode_wrapper.py pour l'exécuteur MiMo (gratuit mimo-auto)
PORT=4097
if ! curl -s --connect-timeout 3 "http://127.0.0.1:$PORT/" >/dev/null 2>&1; then
  pkill -f "mimo serve --port $PORT" 2>/dev/null
  sleep 1
  nohup mimo serve --port $PORT --hostname 127.0.0.1 > /tmp/mimo_serve.log 2>&1 &
  echo "$(date) MiMo serve relance sur $PORT"
else
  echo "$(date) MiMo serve UP sur $PORT"
fi
