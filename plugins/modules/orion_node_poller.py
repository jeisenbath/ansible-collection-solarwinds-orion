#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2022, Josh M. Eisenbath <j.m.eisenbath@gmail.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: orion_node_poller
short_description: Manage Pollers on Nodes in Solarwinds Orion NPM
description:
    - Create/Remove Pollers on Nodes in Orion NPM
    - Note this module is different from M(solarwinds.orion.orion_node_custom_poller), which manages user created custom Orion pollers.
version_added: "1.0.0"
author: "Josh M. Eisenbath (@jeisenbath)"
options:
    state:
        description:
            - The desired state of the poller.
        required: True
        type: str
        choices:
            - present
            - absent
    poller:
        description:
            - Name of the poller.
        required: True
        type: str
    enabled:
        description:
            - Set poller to enabled or disabled.
        type: bool
        default: True
extends_documentation_fragment:
    - solarwinds.orion.orion_auth_options
    - solarwinds.orion.orion_node_options
requirements:
    - orionsdk
    - requests
'''

EXAMPLES = r'''
---
- name: Add Linux SNMP pollers to node
  solarwinds.orion.orion_node_poller:
    hostname: "{{ solarwinds_server }}"
    username: "{{ solarwinds_user }}"
    password: "{{ solarwinds_pass }}"
    name: "{{ node_name }}"
    state: present
    poller: "{{ item.name }}"
    enabled: "{{ item.enabled }}"
  loop:
    - name: N.LoadAverage.SNMP.Linux
      enabled: True
    - name: N.Cpu.SNMP.HrProcessorLoad
      enabled: True
    - name: N.Memory.SNMP.NetSnmpReal
      enabled: True
  delegate_to: localhost

- name: Disable Topology Layer 3 poller on node
  solarwinds.orion.orion_node_poller:
    hostname: "{{ solarwinds_server }}"
    username: "{{ solarwinds_user }}"
    password: "{{ solarwinds_pass }}"
    name: "{{ node_name }}"
    state: present
    poller: N.Topology_Layer3.SNMP.ipNetToMedia
    enabled: False
  delegate_to: localhost

- name: Remove IPv6 Routing Table poller on node
  solarwinds.orion.orion_node_poller:
    hostname: "{{ solarwinds_server }}"
    username: "{{ solarwinds_user }}"
    password: "{{ solarwinds_pass }}"
    name: "{{ node_name }}"
    state: absent
    poller: N.Routing.SNMP.Ipv6RoutingTable
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
        poller=dict(required=True, type='str'),
        enabled=dict(required=False, default=True, type='bool'),
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
            poller = orion.get_poller('N', str(node['nodeid']), module.params['poller'])
            if poller and poller['Enabled'] == module.params['enabled']:
                module.exit_json(changed=False, orion_node=node)
            else:
                if module.check_mode:
                    module.exit_json(changed=True, orion_node=node)
                else:
                    orion.add_poller('N', str(node['nodeid']), module.params['poller'], module.params['enabled'])
                    module.exit_json(changed=True, orion_node=node)
        except Exception as OrionException:
            module.fail_json(msg='Failed to add poller: {0}'.format(str(OrionException)))

    elif module.params['state'] == 'absent':
        try:
            poller = orion.get_poller('N', str(node['nodeid']), module.params['poller'])
            if poller:
                if module.check_mode:
                    module.exit_json(changed=True, orion_node=node)
                else:
                    orion.remove_poller('N', str(node['nodeid']), module.params['poller'])
                    module.exit_json(changed=True, orion_node=node)
            else:
                module.exit_json(changed=False, orion_node=node)
        except Exception as OrionException:
            module.fail_json(msg='Failed to remove poller: {0}'.format(str(OrionException)))

    module.exit_json(changed=False)


if __name__ == "__main__":
    main()
