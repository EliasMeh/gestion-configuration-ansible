package main

import rego.v1

good := {
	"kind": "Deployment",
	"metadata": {"name": "x", "labels": {"nova/environment": "prod"}},
	"spec": {
		"replicas": 2,
		"template": {"spec": {
			"securityContext": {"runAsNonRoot": true},
			"containers": [{"name": "web", "image": "nginx:1.27", "resources": {"limits": {"memory": "64Mi"}}}],
		}},
	},
}

test_good_passes if count(deny) == 0 with input as good

test_latest_refused if {
	bad := json.patch(good, [{"op": "replace", "path": "/spec/template/spec/containers/0/image", "value": "nginx:latest"}])
	count(deny) == 1 with input as bad
}

test_no_limit_refused if {
	bad := json.patch(good, [{"op": "remove", "path": "/spec/template/spec/containers/0/resources"}])
	count(deny) == 1 with input as bad
}

test_prod_one_replica_refused if {
	bad := json.patch(good, [{"op": "replace", "path": "/spec/replicas", "value": 1}])
	count(deny) == 1 with input as bad
}

test_default_secret_refused if {
	count(deny) == 1 with input as {"kind": "Secret", "metadata": {"name": "s"}, "stringData": {"API_TOKEN": "change-me"}}
}
