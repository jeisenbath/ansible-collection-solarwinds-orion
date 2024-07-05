#!/usr/bin/python
# -*- coding: utf-8 -*-

from ansible.module_utils.basic import AnsibleModule
try:
    from orionsdk import SwisClient
    HAS_ORIONSDK = True
except ImportError:
    HAS_ORIONSDK = False

DOCUMENTATION = r'''
---
module: orion_manage_hardware_health
short_description: This module enables or disables hardware health polling on a node in Solarwinds Orion.
version_added: "2.0.1"
author: "Andy B. (@Andyjb8)"
options:
  polling_method:
    description:
      - The polling method to be used for hardware health.
    required: true
    type: int
  state:
    description:
      - Whether to enable (present) or disable (absent) hardware health polling.
    required: true
    choices: ['present', 'absent']
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
- name: Enable hardware health polling on Cisco node
  orion_manage_hardware_health:
    hostname: "server"
    username: "admin"
    password: "pass"
    node_name: "{{ inventory_hostname }}"
    polling_method: 9  # For Cisco
    state: present
  delegate_to: localhost

  - name: Enable hardware health polling on Juniper node
  orion_manage_hardware_health:
    hostname: "server"
    username: "admin"
    password: "pass"
    node_name: "{{ inventory_hostname }}"
    polling_method: 10  # For Juniper
    state: present
  delegate_to: localhost

- name: Disable hardware health polling on Juniper node
  orion_manage_hardware_health:
    hostname: "server"
    username: "admin"
    password: "pass"
    node_name: "{{ inventory_hostname }}"
    state: absent
  delegate_to: localhost
'''

RETURN = r'''
# Default return values
'''

def main():
    module_args = dict(
        hostname=dict(type='str', required=True),
        username=dict(type='str', required=True),
        password=dict(type='str', required=True, no_log=True),
        node_name=dict(type='str', required=False),  # Now accept node_name
        node_id=dict(type='str', required=False),  # Make node_id optional
        polling_method=dict(type='int', required=False),  # Not required for absent state
        state=dict(type='str', required=True, choices=['present', 'absent']),
    )

    module = AnsibleModule(
        argument_spec=module_args,
        required_one_of=[('node_name', 'node_id')],  # Require at least one
        supports_check_mode=True
    )

    if not HAS_ORIONSDK:
        module.fail_json(msg="The orionsdk module is required")

    hostname = module.params['hostname']
    username = module.params['username']
    password = module.params['password']
    node_name = module.params['node_name']
    node_id = module.params['node_id']
    polling_method = module.params.get('polling_method')
    state = module.params['state']

    swis = SwisClient(hostname, username, password)

    # Resolve node_name to node_id if node_name is provided
    if node_name:
        try:
            results = swis.query(f"SELECT NodeID FROM Orion.Nodes WHERE Caption='{node_name}'")
            node_id = "N:" + str(results['results'][0]['NodeID'])
        except Exception as e:
            module.fail_json(msg=f"Failed to resolve node name to ID: {e}")

    try:
        if state == 'present':
            if not polling_method:
                module.fail_json(msg="polling_method is required when state is present")
            swis.invoke('Orion.HardwareHealth.HardwareInfoBase', 'EnableHardwareHealth', node_id, polling_method)
            module.exit_json(changed=True)
        elif state == 'absent':
            swis.invoke('Orion.HardwareHealth.HardwareInfoBase', 'DisableHardwareHealth', node_id)
            module.exit_json(changed=True)
    except Exception as e:
        module.fail_json(msg=str(e))

if __name__ == '__main__':
    main()
