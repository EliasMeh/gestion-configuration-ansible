# nova-lab : fil rouge NOVA Hello Platform (Gestion des configurations, M2)

Ansible configure les machines (socle, k3s, durcissement, accès) ; Helm déploie l'application `nova-hello`
sur deux environnements (Préprod, Prod) à partir d'un seul chart.

## Lancer le laboratoire (Mac Apple Silicon)

1. Installer VirtualBox 7.1+ (version arm64) et Vagrant :
   `brew install --cask virtualbox vagrant`
2. Autoriser le réseau host-only (macOS / Linux uniquement) :
   `sudo mkdir -p /etc/vbox && echo "* 192.168.56.0/24" | sudo tee /etc/vbox/networks.conf`
3. Noms DNS locaux pour le navigateur :
   `echo "192.168.56.21 hello.preprod.nova.local
192.168.56.22 hello.prod.nova.local" | sudo tee -a /etc/hosts`
4. `vagrant up` puis `vagrant snapshot save lab-propre`
5. `vagrant ssh ctrl` puis `cd /vagrant && make all`

`make all` enchaîne : `deps lint keys baseline cluster harden deploy audit`. Chaque cible se lance seule.

## Secrets

Les mots de passe Vault (`ansible/.vault_pass_preprod`, `ansible/.vault_pass_prod`) ne sont jamais versionnés.
S'ils manquent, `make keys` en génère de nouveaux et rechiffre un nouveau jeton pour l'environnement concerné.

## Écarts assumés par rapport au support

| Écart | Raison |
|---|---|
| `helm_arch` / `goss_arch` calculés depuis `ansible_architecture` | Le support télécharge des binaires `amd64` ; sur Mac Apple Silicon les VM sont `arm64`. |
| `synced_folder` monté en `dmode=775,fmode=664` | Évite un `/vagrant` accessible en écriture à tous (Ansible ignorerait `ansible.cfg`) et des `.vault_pass_*` exécutables (Ansible les lancerait comme des scripts). |
| `.editorconfig` : `indent_style = tab` pour le Makefile | `make` exige des tabulations dans les recettes. |
| Goss : test HTTP de l'Ingress au lieu de `port tcp:80 listening` | Le port 80 de k3s passe par des règles iptables (ServiceLB) : aucune socket n'écoute, le test du support échouerait toujours. |
| `assert` sur `env_name` en tête du rôle `common` | Proposition « pour aller plus loin » du TP3. |
| `helm-diff` épinglé (`helm_diff_version: 3.9.14`) | La dernière version du plugin exige un Helm plus récent que 3.16.4 (`unknown field "platformHooks"`). |
| Valeurs Helm construites en une seule expression Jinja | Des `"{{ x \| int }}"` imbriqués arrivent en texte : le schéma refusait `replicaCount: Expected integer, given string`. |
| `no_log` désactivable (`-e nova_no_log=false -e nova_api_token=factice`) | Permet de lire l'erreur Helm sans jamais afficher le vrai secret. |
| `timeout` au lieu de `wait_timeout` | Paramètre déprécié dans kubernetes.core 5. |
| Goss : `tcp6:6443` au lieu de `tcp:6443` | k3s écoute en double pile (`*:6443`). |
| Alignement de `/etc/ufw/sysctl.conf` | ufw remettait `log_martians=0` à chaque rechargement : `harden.yml` n'était pas idempotent. |
| `no_log` levé en `--check`, révision par défaut dans le message | Sinon `deploy.yml --check --diff` (TP9) n'affiche aucun diff et échoue faute de révision. helm-diff masque déjà le contenu des Secrets. |
| Verdict Goss résumé (`Count: …` et détail des seuls échecs) | La boucle `assert` du support affichait toute la sortie de chaque commande (plus de 400 lignes). |
| `apport` ajouté à `hardening_removed_packages` | Il remet `fs.suid_dumpable=2` à chaque démarrage : audit rouge après redémarrage (TP13, scénario 4). |
| `loadBalancerSourceRanges` sur Traefik (`HelmChartConfig`) | ServiceLB publie le port 80 par DNAT, avant ufw : Prod restait joignable depuis Préprod (TP14, PSSI-08). |
| TP13 : réconciliation rendue avec `helm get values` et `--skip-tests` | La commande du support appliquait les valeurs par défaut (Ingress sur le mauvais hôte, 404) et créait le pod de test. |
| TP13 : suppression d'un seul pod | `delete pod -l … \| head -1` supprime tous les pods ; `head` ne tronque que l'affichage. |
| TP11 : `nslookup kubernetes.default.svc.cluster.local` | Le `nslookup` de busybox n'applique pas les domaines de recherche : NXDOMAIN sur le nom court. |
| `helm … --kubeconfig /etc/rancher/k3s/k3s.yaml` dans les commandes ad hoc | Via `ansible -b`, root n'a pas de `KUBECONFIG` : « cluster unreachable ». |
