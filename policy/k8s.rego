# Politique NOVA sur les manifestes Kubernetes produits par `helm template`.
package main

import rego.v1

containers := input.spec.template.spec.containers

deny contains msg if {
	input.kind == "Deployment"
	some c in containers
	not c.resources.limits.memory
	msg := sprintf("Deployment %s : le conteneur %s n'a pas de limite de mémoire", [input.metadata.name, c.name])
}

deny contains msg if {
	input.kind == "Deployment"
	some c in containers
	endswith(c.image, ":latest")
	msg := sprintf("Deployment %s : l'image %s utilise le tag latest", [input.metadata.name, c.image])
}

deny contains msg if {
	input.kind == "Deployment"
	some c in containers
	not contains(c.image, ":")
	msg := sprintf("Deployment %s : l'image %s n'a pas de tag explicite", [input.metadata.name, c.image])
}

deny contains msg if {
	input.kind == "Deployment"
	not input.spec.template.spec.securityContext.runAsNonRoot == true
	msg := sprintf("Deployment %s : le pod doit s'exécuter en non-root", [input.metadata.name])
}

deny contains msg if {
	input.kind == "Secret"
	input.stringData.API_TOKEN == "change-me"
	msg := sprintf("Secret %s : le jeton par défaut 'change-me' n'a pas été remplacé", [input.metadata.name])
}

deny contains msg if {
	input.kind == "Deployment"
	input.metadata.labels["nova/environment"] == "prod"
	input.spec.replicas < 2
	msg := sprintf("Deployment %s : la production exige au moins 2 réplicas", [input.metadata.name])
}
