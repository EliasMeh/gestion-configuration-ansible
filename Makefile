# Makefile : orchestration de bout en bout du laboratoire NOVA (TP15)
# À lancer depuis la VM ctrl :  cd /vagrant && make all
ANSIBLE_DIR := /vagrant/ansible
export ANSIBLE_CONFIG := $(ANSIBLE_DIR)/ansible.cfg
PLAY := cd $(ANSIBLE_DIR) && ansible-playbook

.PHONY: all deps lint keys baseline cluster harden deploy audit

all: deps lint keys baseline cluster harden deploy audit

deps:
	cd $(ANSIBLE_DIR) && ansible-galaxy collection install -r requirements.yml

lint:
	cd $(ANSIBLE_DIR) && yamllint -c /vagrant/.yamllint .
	cd $(ANSIBLE_DIR) && ansible-lint -c /vagrant/.ansible-lint playbooks roles
	helm lint /vagrant/charts/nova-hello -f /vagrant/charts/nova-hello/values-prod.yaml

# Mots de passe Vault (hors Git) et clés des comptes nominatifs.
# Si un mot de passe manque, le vault.yml de l'environnement est régénéré avec un nouveau jeton.
keys:
	for env in preprod prod; do \
	  pass=$(ANSIBLE_DIR)/.vault_pass_$$env; \
	  if [ ! -s $$pass ]; then \
	    openssl rand -base64 24 | tr -d '\n' > $$pass; chmod 600 $$pass; \
	    rm -f $(ANSIBLE_DIR)/inventories/group_vars/$$env/vault.yml; \
	    bash /vagrant/scripts/rotate-token.sh $$env; \
	  fi; \
	done
	for u in alice bob; do \
	  [ -f $$HOME/.ssh/$$u ] || ssh-keygen -q -t ed25519 -N "" -C "$$u@nova" -f $$HOME/.ssh/$$u; \
	done

baseline:
	$(PLAY) playbooks/baseline.yml

cluster:
	$(PLAY) playbooks/cluster.yml

harden:
	$(PLAY) playbooks/harden.yml --skip-tags firewall
	$(PLAY) playbooks/harden.yml --tags firewall

deploy:
	$(PLAY) playbooks/deploy.yml -e nova_require_approval=false

audit:
	$(PLAY) playbooks/audit.yml
