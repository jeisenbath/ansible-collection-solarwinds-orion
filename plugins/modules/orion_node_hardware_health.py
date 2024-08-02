#!/usr/bin/python
# -*- coding: utf-8 -*-
from ansible_collections.solarwinds.orion.plugins.module_utils.orion import OrionModule, orion_argument_spec
from ansible.module_utils.basic import AnsibleModule
try:
    from orionsdk import SwisClient
    HAS_ORIONSDK = True
except ImportError:
    HAS_ORIONSDK = False

DOCUMENTATION = r'''
---
module: orion_manage_hardware_health
short_description: Manage hardware health polling on a node in Solarwinds Orion
description:
    - This module enables or disables hardware health polling on a node in Solarwinds Orion.
author: "Andrew Bailey (@Andyjb8)"
requirements:
    - orionsdk
options:
    hostname:
        description:
            - The Orion server hostname.
        required: True
        type: str
    username:
        description:
            - The Orion username.
        required: True
        type: str
    password:
        description:
            - The Orion password.
        required: True
        type: str
    name: 
        description:
            - The Caption in Orion.
        required: True if node_id not specified
        type: str
    node_id: 
        description:
            - The node_id in Orion.
        required: True if name not specified
        type: str
    polling_method:
        description:
            - The polling method to be used for hardware health.
        required: True when state is present
        choices: ['Unknown', 'VMware', 'SnmpDell', 'SnmpHP', 'SnmpIBM', 'VMwareAPI', 'WmiDell', 'WmiHP', 'WmiIBM', 'SnmpCisco', 'SnmpJuniper', 'SnmpNPMHP', 'SnmpF5', 'SnmpDellPowerEdge', 'SnmpDellPowerConnect', 'SnmpDellBladeChassis', 'SnmpHPBladeChassis', 'Forwarded', 'SnmpArista']
        type: str
    state:
        description:
            - Whether to enable (present) or disable (absent) hardware health polling.
        required: True
        choices: ['present', 'absent']
        type: str
'''

EXAMPLES = r'''
---
- name: Enable hardware health polling on Cisco node
  orion_manage_hardware_health:
    hostname: "server"
    username: "admin"
    password: "pass"
    name: "{{ inventory_hostname }}"
    polling_method: SnmpCisco
    state: present
  delegate_to: localhost

- name: Disable hardware health polling on Juniper node
  orion_manage_hardware_health:
    hostname: "server"
    username: "admin"
    password: "pass"
    name: "{{ inventory_hostname }}"
    state: absent
  delegate_to: localhost
'''

RETURN = r'''
# Default return values
'''

# Mapping of polling method names to their corresponding IDs
POLLING_METHOD_MAP = {
    'Unknown': 0,
    'VMware': 1,
    'SnmpDell': 2,
    'SnmpHP': 3,
    'SnmpIBM': 4,
    'VMwareAPI': 5,
    'WmiDell': 6,
    'WmiHP': 7,
    'WmiIBM': 8,
    'SnmpCisco': 9,
    'SnmpJuniper': 10,
    'SnmpNPMHP': 11,
    'SnmpF5': 12,
    'SnmpDellPowerEdge': 13,
    'SnmpDellPowerConnect': 14,
    'SnmpDellBladeChassis': 15,
    'SnmpHPBladeChassis': 16,
    'Forwarded': 17,
    'SnmpArista': 18
}

def main():
    argument_spec = orion_argument_spec
    argument_spec.update(
        state=dict(required=True, choices=['present', 'absent']),
        polling_method=dict(type='str', required=False, choices=list(POLLING_METHOD_MAP.keys())),  # Not required for absent state
        name=dict(type='str', required=False, aliases=['caption']),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        required_one_of=[('name', 'node_id')],  # Require at least one
        supports_check_mode=True
    )

    if not HAS_ORIONSDK:
        module.fail_json(msg="The orionsdk module is required")

    orion = OrionModule(module)

    name = module.params['name']
    node_id = module.params['node_id']
    state = module.params['state']
    polling_method = module.params.get('polling_method')

    if name:
        try:
            results = orion.swis_query(f"SELECT NodeID FROM Orion.Nodes WHERE Caption='{name}'")
            node_id = "N:" + str(results[0]['NodeID'])
        except Exception as e:
            module.fail_json(msg=f"Failed to resolve node name to ID: {e}")

    try:
        if state == 'present':
            if not polling_method:
                module.fail_json(msg="polling_method is required when state is present")
            polling_method_id = POLLING_METHOD_MAP[polling_method]
            if orion.swis.invoke('Orion.HardwareHealth.HardwareInfoBase', 'IsHardwareHealthEnabled', node_id, polling_method_id):
                module.exit_json(changed=False)
            orion.swis.invoke('Orion.HardwareHealth.HardwareInfoBase', 'EnableHardwareHealth', node_id, polling_method_id)
            module.exit_json(changed=True)
        elif state == 'absent':
            orion.swis.invoke('Orion.HardwareHealth.HardwareInfoBase', 'DisableHardwareHealth', node_id)
            module.exit_json(changed=True)
    except Exception as e:
        module.fail_json(msg=str(e))

if __name__ == '__main__':
    main()
