#!/usr/bin/python
# -*- coding: utf-8 -*-

# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: orion_node_hardware_health
short_description: Manage hardware health polling on a node in Solarwinds Orion
description:
    - This module enables or disables hardware health polling on a node in Solarwinds Orion.
author: "Andrew Bailey (@Andyjb8)"
requirements:
    - orionsdk
options:
    polling_method:
        description:
            - The polling method to be used for hardware health.
            - Required when I(state=present)
        required: False
        choices:
            - 'Unknown'
            - 'VMware'
            - 'SnmpDell'
            - 'SnmpHP'
            - 'SnmpIBM'
            - 'VMwareAPI'
            - 'WmiDell'
            - 'WmiHP'
            - 'WmiIBM'
            - 'SnmpCisco'
            - 'SnmpJuniper'
            - 'SnmpNPMHP'
            - 'SnmpF5'
            - 'SnmpDellPowerEdge'
            - 'SnmpDellPowerConnect'
            - 'SnmpDellBladeChassis'
            - 'SnmpHPBladeChassis'
            - 'Forwarded'
            - 'SnmpArista'
        type: str
    state:
        description:
            - Whether to enable (present) or disable (absent) hardware health polling.
        required: True
        choices: ['present', 'absent']
        type: str
extends_documentation_fragment:
    - jeisenbath.solarwinds.orion_auth_options
    - jeisenbath.solarwinds.orion_node_options
'''

EXAMPLES = r'''
---
- name: Enable hardware health polling on Cisco node
  jeisenbath.solarwinds.orion_node_hardware_health:
    hostname: "server"
    username: "admin"
    password: "pass"
    name: "{{ inventory_hostname }}"
    polling_method: SnmpCisco
    state: present
  delegate_to: localhost

- name: Disable hardware health polling on Juniper node
  jeisenbath.solarwinds.orion_node_hardware_health:
    hostname: "server"
    username: "admin"
    password: "pass"
    name: "{{ inventory_hostname }}"
    state: absent
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
        "lastsystemuptimepollutc": "2024-09-25T18:34:20.7630000Z",
        "netobjectid": "N:12345",
        "nodeid": "12345",
        "objectsubtype": "SNMP",
        "status": 1,
        "statusdescription": "Node status is Up.",
        "unmanaged": false,
        "unmanagefrom": "1899-12-30TO00:00:00+00:00",
        "unmanageuntil": "1899-12-30TO00:00:00+00:00",
        "uri": "swis://host.domain.com/Orion/Orion.Nodes/NodeID=12345"
    }
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.jeisenbath.solarwinds.plugins.module_utils.orion import OrionModule, orion_argument_spec
try:
    import requests
    HAS_REQUESTS = True
    requests.packages.urllib3.disable_warnings()
except ImportError:
    HAS_REQUESTS = False
except Exception:
    raise Exception


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
    argument_spec = orion_argument_spec()
    argument_spec.update(
        state=dict(required=True, choices=['present', 'absent']),
        polling_method=dict(type='str', required=False, choices=list(POLLING_METHOD_MAP.keys())),  # Not required for absent state
    )
    module = AnsibleModule(
        argument_spec,
        required_one_of=[('name', 'node_id', 'ip_address')],
        supports_check_mode=True,
        required_if=[
            ('state', 'present', ['polling_method'])
        ],
    )

    orion = OrionModule(module)
    node = orion.get_node()
    if not node:
        module.fail_json(skipped=True, msg='Node not found')
    changed = False

    try:
        hh_poller = orion.swis_query("SELECT PollingMethod FROM Orion.HardwareHealth.HardwareInfoBase WHERE ParentObjectID = '{0}'".format(node['nodeid']))
        if module.params['state'] == 'present':
            polling_method_id = POLLING_METHOD_MAP[module.params['polling_method']]
            if not hh_poller:
                if not module.check_mode:
                    orion.swis.invoke('Orion.HardwareHealth.HardwareInfoBase', 'EnableHardwareHealth', node['netobjectid'], polling_method_id)
                changed = True
            elif hh_poller[0]['PollingMethod'] != polling_method_id:
                module.fail_json(msg="HardwareHealth montior exists, but does not match provided polling_method parameter.")
        elif module.params['state'] == 'absent':
            if hh_poller:
                if not module.check_mode:
                    orion.swis.invoke('Orion.HardwareHealth.HardwareInfoBase', 'DisableHardwareHealth', node['netobjectid'])
                changed = True
    except Exception as e:
        module.fail_json(msg=str(e))

    module.exit_json(changed=changed, orion_node=node)


if __name__ == '__main__':
    main()
