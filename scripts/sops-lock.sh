#!/usr/bin/env bash
# sops-lock.sh : efface de la mémoire les clés age chargées par sops-env.sh
set -euo pipefail
DIR="/dev/shm/sops-$(id -u)"
if [ -f "$DIR/keys.txt" ]; then
  shred -u "$DIR/keys.txt" 2>/dev/null || rm -f "$DIR/keys.txt"
  echo "clés effacées de $DIR" >&2
fi
