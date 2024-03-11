#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2022, Josh M. Eisenbath <j.m.eisenbath@gmail.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: orion_node_interface
short_description: Manage interfaces on Nodes in Solarwinds Orion NPM
description:
    - Add or remove an interface on a Node in Orion NPM.
    - Adding an interface will run a discovery on the node to find available interfaces.
version_added: "1.0.0"
author: "Josh M. Eisenbath (@jeisenbath)"
options:
    state:
        description:
            - The desired state of the interface.
        required: True
        type: str
        choices:
            - present
            - absent
    interface:
        description:
            - The name of the interface.
            - If omitted, the module will discover and manage all interfaces.
        required: False
        type: str
    regex:
        description:
            - Whether or not to use regex pattern matching for I(interface).
            - When I(regex=true), check mode will always show changed.
        required: False
        type: bool
        default: False
extends_documentation_fragment:
    - solarwinds.orion.orion_auth_options
    - solarwinds.orion.orion_node_options
requirements:
    - orionsdk
    - requests
'''

EXAMPLES = r'''
---

- name: Discover and add all interfaces to node
  solarwinds.orion.orion_node_interface:
    hostname: "{{ solarwinds_server }}"
    username: "{{ solarwinds_user }}"
    password: "{{ solarwinds_pass }}"
    name: "{{ node_name }}"
    state: present
  delegate_to: localhost

- name: Add all interfaces matching regex pattern "Ethernet [0-9]$"
  solarwinds.orion.orion_node_interface:
    hostname: "{{ solarwinds_server }}"
    username: "{{ solarwinds_user }}"
    password: "{{ solarwinds_pass }}"
    name: "{{ node_name }}"
    state: present
    interface: "Ethernet [0-9]$"
    regex: true
  delegate_to: localhost

- name: Remove an interface from node
  solarwinds.orion.orion_node_interface:
    hostname: "{{ solarwinds_server }}"
    username: "{{ solarwinds_user }}"
    password: "{{ solarwinds_pass }}"
    name: "{{ node_name }}"
    state: absent
    interface: "{{ interface_name }}"
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
discovered:
    description: List of discovered interfaces.
    returned: always
    type: list
    elements: dict
    sample: [
            {
                "Caption": "lo",
                "InterfaceID": 0,
                "Manageable": true,
                "ifAdminStatus": 1,
                "ifIndex": 1,
                "ifOperStatus": 1,
                "ifSpeed": 0.0,
                "ifSubType": 0,
                "ifType": 24
            },
            {
                "Caption": "eth0",
                "InterfaceID": 268420,
                "Manageable": true,
                "ifAdminStatus": 1,
                "ifIndex": 2,
                "ifOperStatus": 1,
                "ifSpeed": 0.0,
                "ifSubType": 0,
                "ifType": 6
            }
        ]
interfaces:
    description: Interfaces added or removed by task.
    returned: always, except for when I(state=present), I(interface) is defined and running in check mode.
    type: list
    elements: dict
    sample: [
            {
                "Caption": "lo",
                "InterfaceID": 0,
                "Manageable": true,
                "ifAdminStatus": 1,
                "ifIndex": 1,
                "ifOperStatus": 1,
                "ifSpeed": 0.0,
                "ifSubType": 0,
                "ifType": 24
            }
        ]
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
        interface=dict(required=False, type='str'),
        regex=dict(required=False, type=bool, default=False),
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

    changed = False
    discovered = orion.discover_interfaces(node)
    interfaces = []
    if module.params['state'] == 'present':
        try:
            if not module.params['interface']:
                for interface in discovered:
                    if not orion.get_interface(node, interface['Caption']):
                        changed = True
                        interfaces.append(interface)
                        if not module.check_mode:
                            orion.add_interface(node, interface['Caption'], False, discovered)
            else:
                get_int = orion.get_interface(node, module.params['interface'])
                if not get_int:
                    if module.check_mode:
                        changed = True
                    else:
                        interfaces = orion.add_interface(node, module.params['interface'], module.params['regex'], discovered)
                        if interfaces:
                            changed = True
        except Exception as OrionException:
            module.fail_json(msg='Failed to add interfaces: {0}'.format(str(OrionException)))
    elif module.params['state'] == 'absent':
        try:
            if not module.params['interface']:
                for interface in discovered:
                    if orion.get_interface(node, interface['Caption']):
                        changed = True
                        interfaces.append(interface)
                        if not module.check_mode:
                            orion.remove_interface(node, interface['Caption'])
            else:
                get_int = orion.get_interface(node, module.params['interface'])
                if get_int:
                    changed = True
                    interfaces.append(get_int)
                    if not module.check_mode:
                        orion.remove_interface(node, module.params['interface'])

        except Exception as OrionException:
            module.fail_json(msg='Failed to remove interface: {0}'.format(str(OrionException)))

    module.exit_json(changed=changed, orion_node=node, discovered=discovered, interfaces=interfaces)


if __name__ == "__main__":
    main()
