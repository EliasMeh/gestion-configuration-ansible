# Politique sur la CMDB (ansible/inventories/cmdb.json) : chaque serveur est exploitable et attribué.
package cmdb

import rego.v1

deny contains msg if {
	some s in input.servers
	not s.owner
	msg := sprintf("%s : aucun propriétaire dans la CMDB", [s.hostname])
}

deny contains msg if {
	some s in input.servers
	not s.criticality in {"low", "medium", "high"}
	msg := sprintf("%s : criticité absente ou invalide", [s.hostname])
}

deny contains msg if {
	some s in input.servers
	s.criticality == "high"
	not s.maintenance_window
	msg := sprintf("%s : un serveur critique doit avoir une fenêtre de maintenance", [s.hostname])
}

deny contains msg if {
	some s in input.servers
	not startswith(s.hostname, "node-")
	msg := sprintf("%s : le nom doit commencer par node-", [s.hostname])
}
