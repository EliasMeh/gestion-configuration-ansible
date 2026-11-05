#!/usr/bin/env bash
# policy-check.sh : applique les politiques NOVA avant tout déploiement.
#   1. manifestes rendus par helm  2. CMDB  3. variables de chaque environnement
set -euo pipefail
cd "${NOVA_ROOT:-/vagrant}"
rc=0
for chart in charts/nova-hello charts/nova-platform; do
  for env in preprod prod; do
    vals="$chart/values-$env.yaml"; [ -f "$vals" ] || continue
    echo "== $chart ($env)"
    # Le vrai jeton n'est jamais dans les valeurs : Ansible l'injecte au déploiement (SOPS).
    # On simule cette injection, sauf si le fichier de valeurs fixe lui-même un jeton (contrôlé alors).
    tok=(); grep -q "apiToken" "$vals" || tok=(--set secret.apiToken=injecte-au-deploiement --set nova-hello.secret.apiToken=injecte-au-deploiement)
    helm template check "$chart" -f "$vals" "${tok[@]}" | conftest test --policy policy --namespace main - || rc=1
  done
done
echo "== CMDB"
conftest test ansible/inventories/cmdb.json --policy policy --namespace cmdb || rc=1
for env in preprod prod; do
  echo "== group_vars/$env"
  conftest test "ansible/inventories/group_vars/$env/main.yml" --policy policy --namespace groupvars || rc=1
done
exit $rc
