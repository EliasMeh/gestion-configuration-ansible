#!/usr/bin/env python3
"""Inventaire dynamique NOVA : lit la CMDB (cmdb.json) et produit le JSON attendu par Ansible."""
import argparse
import json
import os
import re
import sys

CMDB = os.environ.get("NOVA_CMDB", os.path.join(os.path.dirname(os.path.abspath(__file__)), "cmdb.json"))


def slug(value):
    """Un nom de groupe Ansible ne doit contenir que lettres, chiffres et underscores."""
    return re.sub(r"[^a-zA-Z0-9_]", "_", str(value))


def build(servers):
    inv = {"_meta": {"hostvars": {}}, "all": {"children": ["nova", "ungrouped"]}, "nova": {"children": []}}

    def add(group, host):
        inv.setdefault(group, {"hosts": []}).setdefault("hosts", []).append(host)

    for srv in servers:
        host = srv["hostname"]
        inv["_meta"]["hostvars"][host] = {
            "ansible_host": srv["ip"],
            "cmdb_owner": srv.get("owner", "inconnu"),
            "cmdb_criticality": srv.get("criticality", "medium"),
            "cmdb_maintenance_window": srv.get("maintenance_window", "non défini"),
        }
        add(slug(srv["env"]), host)                         # groupes d'environnement : preprod, prod
        if slug(srv["env"]) not in inv["nova"]["children"]:
            inv["nova"]["children"].append(slug(srv["env"]))
        for role in srv.get("roles", []):
            add("role_" + slug(role), host)                 # groupes par rôle technique
        add("crit_" + slug(srv.get("criticality", "medium")), host)   # groupes par criticité
        add("owner_" + slug(srv.get("owner", "inconnu")), host)       # groupes par propriétaire
    inv["ungrouped"] = {"hosts": []}
    return inv


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--list", action="store_true")
    parser.add_argument("--host")
    args = parser.parse_args()
    try:
        with open(CMDB, encoding="utf-8") as fh:
            servers = json.load(fh)["servers"]
    except (OSError, KeyError, ValueError) as exc:
        sys.stderr.write("Erreur CMDB (%s) : %s\n" % (CMDB, exc))
        return 1
    inv = build(servers)
    if args.host:
        print(json.dumps(inv["_meta"]["hostvars"].get(args.host, {})))
    else:
        print(json.dumps(inv, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
