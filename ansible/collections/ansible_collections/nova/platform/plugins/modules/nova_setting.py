#!/usr/bin/python
# -*- coding: utf-8 -*-
# GNU General Public License v3.0+
from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
module: nova_setting
short_description: Garantit qu'une clé vaut une valeur dans un fichier « clé = valeur »
description:
  - Ajoute, modifie ou retire une ligne C(clé = valeur), sans toucher au reste du fichier.
  - Idempotent, compatible C(--check) et C(--diff). Avec O(secret=true), la valeur est masquée.
options:
  path: {description: Fichier de configuration., type: path, required: true}
  key: {description: Nom de la clé., type: str, required: true}
  value: {description: Valeur voulue (obligatoire si state=present)., type: str}
  state: {description: Présence ou absence de la clé., type: str, default: present, choices: [present, absent]}
  secret: {description: Masquer la valeur dans le diff et le résultat., type: bool, default: false}
extends_documentation_fragment: [files]
author: Equipe plateforme NOVA
'''

EXAMPLES = r'''
- name: Niveau de journalisation
  nova.platform.nova_setting:
    path: /etc/nova/app.conf
    key: log_level
    value: info
    mode: "0640"
'''

RETURN = r'''
changed_key: {description: Clé modifiée (vide si rien n'a changé)., type: str, returned: always}
previous: {description: Ancienne valeur (jamais pour un secret)., type: str, returned: changed and not secret}
'''

import os
import re

from ansible.module_utils.basic import AnsibleModule


def parse(lines, key):
    """Renvoie (index, valeur) de la clé dans les lignes, ou (None, None) si absente."""
    pattern = re.compile(r'^\s*' + re.escape(key) + r'\s*=\s*(.*?)\s*$')
    for idx, line in enumerate(lines):
        match = pattern.match(line)
        if match:
            return idx, match.group(1)
    return None, None


def main():
    module = AnsibleModule(
        argument_spec=dict(
            path=dict(type='path', required=True),
            key=dict(type='str', required=True, no_log=False),
            value=dict(type='str'),
            state=dict(type='str', default='present', choices=['present', 'absent']),
            secret=dict(type='bool', default=False, no_log=False),
        ),
        required_if=[('state', 'present', ['value'])],
        add_file_common_args=True,
        supports_check_mode=True,
    )
    path, key, value, state = module.params['path'], module.params['key'], module.params['value'], module.params['state']
    secret = module.params['secret']
    if value is not None and '\n' in value:
        module.fail_json(msg='La valeur ne doit pas contenir de saut de ligne.')

    lines = []
    if os.path.exists(path):
        with open(path, encoding='utf-8') as fh:
            lines = fh.read().splitlines()
    before = list(lines)
    idx, current = parse(lines, key)

    if state == 'present':
        new_line = '%s = %s' % (key, value)
        if idx is None:
            lines.append(new_line)
        elif current != value:
            lines[idx] = new_line
    elif idx is not None:
        del lines[idx]

    changed = lines != before
    result = dict(changed=changed, changed_key=key if changed else '')
    if changed and not secret and current is not None:
        result['previous'] = current
    if module._diff:
        mask = (lambda ls: [re.sub(r'=.*$', '= ********', ln) if re.match(r'^\s*' + re.escape(key) + r'\s*=', ln) else ln for ln in ls]) \
            if secret else (lambda ls: ls)
        result['diff'] = dict(before='\n'.join(mask(before)) + '\n', after='\n'.join(mask(lines)) + '\n',
                              before_header=path, after_header=path)

    if changed and not module.check_mode:
        os.makedirs(os.path.dirname(path) or '.', exist_ok=True)
        with open(path, 'w', encoding='utf-8') as fh:
            fh.write('\n'.join(lines) + '\n')
    file_args = module.load_file_common_arguments(module.params, path=path)
    if os.path.exists(path) or not module.check_mode:
        result['changed'] = module.set_fs_attributes_if_different(file_args, result['changed'])
    module.exit_json(**result)


if __name__ == '__main__':
    main()
