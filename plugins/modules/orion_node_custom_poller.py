#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2022, Josh M. Eisenbath <j.m.eisenbath@gmail.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: orion_node_custom_poller
short_description: Creates/Removes custom pollers to a Node in Solarwinds Orion NPM
description:
    - This module will add or remove a custom poller to a Node in Solarwinds Orion NPM.
    - The custom poller must already exist to be added to the node.
    - Note this module is different from M(solarwinds.orion.orion_node_poller), which manages standard Orion pollers.
version_added: "1.0.0"
author: "Josh M. Eisenbath (@jeisenbath)"
options:
    state:
        description:
            - The desired state of the custom poller.
        required: True
        type: str
        choices:
            - present
            - absent
    custom_poller:
        description:
            - The name of the custom poller.
        required: True
        type: str
extends_documentation_fragment:
    - solarwinds.orion.orion_auth_options
    - solarwinds.orion.orion_node_options
requirements:
    - orionsdk
    - requests
'''

EXAMPLES = r'''
---

- name: Add custom pollers to node
  solarwinds.orion.orion_node_custom_poller:
    hostname: "{{ solarwinds_server }}"
    username: "{{ solarwinds_user }}"
    password: "{{ solarwinds_pass }}"
    name: "{{ node_name }}"
    state: present
    custom_poller: "{{ custom_poller_name }}"
  delegate_to: localhost

'''

RETURN = r'''
orion_node:
    description: Info about an orion node.
    returned: always
    type: dict
    sample: {
        "caption": "localhost",
        "ipaddress": "127.0.0.1",
        "netobjectid": "N:12345",
        "nodeid": "12345",
        "objectsubtype": "SNMP",
        "status": 1,
        "statusdescription": "Node status is Up.",
        "unmanaged": false,
        "unmanagefrom": "1899-12-30T00:00:00+00:00",
        "unmanageuntil": "1899-12-30T00:00:00+00:00",
        "uri": "swis://host.domain.com/Orion/Orion.Nodes/NodeID=12345"
    }
'''

import requests
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.solarwinds.orion.plugins.module_utils.orion import OrionModule, orion_argument_spec
try:
    from orionsdk import SwisClient
    HAS_ORION = True
except ImportError:
    HAS_ORION = False
except Exception:
    raise Exception

requests.packages.urllib3.disable_warnings()


def main():
    argument_spec = orion_argument_spec
    argument_spec.update(
        state=dict(required=True, choices=['present', 'absent']),
        custom_poller=dict(required=True, type='str')
    )
    module = AnsibleModule(
        argument_spec,
        supports_check_mode=True,
        required_one_of=[('name', 'node_id', 'ip_address')],
    )
    if not HAS_ORION:
        module.fail_json(msg='orionsdk required for this module')

    options = {
        'hostname': module.params['hostname'],
        'username': module.params['username'],
        'password': module.params['password'],
    }

    __SWIS__ = SwisClient(**options)

    try:
        __SWIS__.query('SELECT uri FROM Orion.Environment')
    except Exception as AuthException:
        module.fail_json(
            msg='Failed to query Orion. '
                'Check Hostname, Username, and/or Password: {0}'.format(str(AuthException))
        )

    orion = OrionModule(module, __SWIS__)

    node = orion.get_node()
    if not node:
        module.fail_json(skipped=True, msg='Node not found')

    if module.params['state'] == 'present':
        try:
            if not orion.get_custom_poller_id(module.params['custom_poller']):
                module.fail_json(msg='Custom poller {0} not found.'.format(module.params['custom_poller']))
        except Exception as OrionException:
            module.fail_json(msg='Failed to query for custom poller: {0}'.format(str(OrionException)))

        try:
            if orion.get_custom_poller_uri(node, module.params['custom_poller']):
                module.exit_json(changed=False, orion_node=node)
            else:
                if module.check_mode:
                    module.exit_json(changed=True, orion_node=node)
                else:
                    orion.add_custom_poller(node, module.params['custom_poller'])
                    module.exit_json(changed=True, orion_node=node)
        except Exception as OrionException:
            module.fail_json(msg='Failed to create custom poller: {0}'.format(str(OrionException)))
    elif module.params['state'] == 'absent':
        try:
            if not orion.get_custom_poller_uri(node, module.params['custom_poller']):
                module.exit_json(changed=False, orion_node=node)
            else:
                if module.check_mode:
                    module.exit_json(changed=True, orion_node=node)
                else:
                    orion.remove_custom_poller(node, module.params['custom_poller'])
                    module.exit_json(changed=True, orion_node=node)
        except Exception as OrionException:
            module.fail_json(msg='Failed to remove custom poller: {0}'.format(str(OrionException)))
    # TODO create custom pollers
    else:
        module.exit_json(changed=False)


if __name__ == "__main__":
    main()
