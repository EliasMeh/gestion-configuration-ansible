# -*- coding: utf-8 -*-
# GNU General Public License v3.0+
from __future__ import absolute_import, division, print_function
__metaclass__ = type

import re

from ansible.errors import AnsibleFilterError

DOCUMENTATION = r'''
name: nova_mask
short_description: Masque une valeur secrète en gardant les derniers caractères
description:
  - Utile pour afficher un jeton dans un rapport sans le divulguer.
positional: _input
options:
  _input:
    description: Valeur à masquer.
    type: str
    required: true
  keep:
    description: Nombre de caractères conservés à la fin.
    type: int
    default: 4
'''

EXAMPLES = r'''
- ansible.builtin.debug:
    msg: "{{ 'tok-prod-1234567890' | nova.platform.nova_mask }}"   # ***************7890
'''

RETURN = r'''
_value:
  description: Valeur masquée.
  type: str
'''


def nova_mask(value, keep=4):
    value = str(value)
    if keep < 0:
        raise AnsibleFilterError('nova_mask : keep doit être positif')
    if len(value) <= keep:
        return '*' * len(value)
    return '*' * (len(value) - keep) + value[-keep:]


def nova_semver_bump(version, part='patch'):
    match = re.match(r'^(\d+)\.(\d+)\.(\d+)$', str(version))
    if not match:
        raise AnsibleFilterError('nova_semver_bump : "%s" n\'est pas une version X.Y.Z' % version)
    major, minor, patch = (int(x) for x in match.groups())
    if part == 'major':
        return '%d.0.0' % (major + 1)
    if part == 'minor':
        return '%d.%d.0' % (major, minor + 1)
    if part == 'patch':
        return '%d.%d.%d' % (major, minor, patch + 1)
    raise AnsibleFilterError('nova_semver_bump : part doit être major, minor ou patch')


class FilterModule(object):
    def filters(self):
        return {'nova_mask': nova_mask, 'nova_semver_bump': nova_semver_bump}
