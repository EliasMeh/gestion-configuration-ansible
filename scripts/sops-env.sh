#!/usr/bin/env bash
# sops-env.sh <env>... : met en mémoire (tmpfs) les clés age des seuls environnements demandés
# et affiche la commande export à exécuter. Usage : eval "$(scripts/sops-env.sh preprod)"
set -euo pipefail
[ $# -ge 1 ] || { echo "usage : eval \"\$($0 preprod [prod])\"" >&2; exit 2; }
DIR="/dev/shm/sops-$(id -u)"
mkdir -p "$DIR" && chmod 700 "$DIR"
umask 077
: > "$DIR/keys.txt"
for e in "$@"; do
  src="$HOME/.config/sops/age/$e.txt"
  [ -s "$src" ] || { echo "clé introuvable : $src" >&2; exit 2; }
  cat "$src" >> "$DIR/keys.txt"
done
echo "export SOPS_AGE_KEY_FILE=$DIR/keys.txt"
echo "clés chargées pour : $*" >&2
