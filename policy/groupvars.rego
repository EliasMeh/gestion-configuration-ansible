# Politique sur les variables d'un environnement (group_vars/<env>/main.yml).
package groupvars

import rego.v1

deny contains msg if {
	input.env_name == "prod"
	input.nova_replicas < 2
	msg := "prod : nova_replicas doit valoir au moins 2"
}

deny contains msg if {
	input.env_name == "prod"
	not input.nova_network_policy == true
	msg := "prod : nova_network_policy doit être activée"
}

deny contains msg if {
	input.nova_image_tag == "latest"
	msg := "nova_image_tag ne doit jamais valoir latest"
}
