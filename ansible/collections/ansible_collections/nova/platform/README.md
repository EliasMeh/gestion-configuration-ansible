# Collection nova.platform

Outils internes de l'équipe plateforme NOVA.

- `nova.platform.nova_setting` : garantit « la clé K vaut V » dans un fichier `clé = valeur`
  (idempotent, `--check`, `--diff`, option `secret` qui masque la valeur).
- Filtres `nova.platform.nova_mask` et `nova.platform.nova_semver_bump`.

Tests : `python3 -m pytest -q tests/unit` depuis la racine du dépôt.
