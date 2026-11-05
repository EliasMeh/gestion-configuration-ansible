# Tests unitaires des filtres de la collection nova.platform : fonctions pures, testées sans Ansible.
import pytest
from ansible.errors import AnsibleFilterError

from ansible_collections.nova.platform.plugins.filter.nova_filters import nova_mask, nova_semver_bump


def test_mask_garde_les_4_derniers():
    assert nova_mask("tok-prod-1234567890") == "*" * 15 + "7890"


def test_mask_valeur_courte_entierement_masquee():
    assert nova_mask("abc") == "***"


def test_mask_keep_negatif_refuse():
    with pytest.raises(AnsibleFilterError):
        nova_mask("secret", keep=-1)


@pytest.mark.parametrize("part, attendu", [("major", "2.0.0"), ("minor", "1.5.0")])
def test_semver_major_minor(part, attendu):
    assert nova_semver_bump("1.4.7", part) == attendu


def test_semver_patch_par_defaut():
    assert nova_semver_bump("1.4.7") == "1.4.8"
