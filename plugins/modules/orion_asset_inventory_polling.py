#!/usr/bin/python
# -*- coding: utf-8 -*-

# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: orion_asset_inventory_polling
short_description: Enable or disable a node to poll Asset Inventory
description:
    - Enables or disables a node to be polled in Orion AssetInventory.
version_added: "3.3.0"
author: "Josh Eisenbath (@jeisenbath)"
requirements:
    - orionsdk
options:
    state:
        description:
            - Whether to enable (present) or disable (absent) Asset Inventory polling.
        required: True
        choices: ['present', 'absent']
        type: str
extends_documentation_fragment:
    - jeisenbath.solarwinds.orion_auth_options
    - jeisenbath.solarwinds.orion_node_options
'''

EXAMPLES = r'''
---
- name: Enable Asset Inventory polling for host
  jeisenbath.solarwinds.orion_asset_inventory_polling:
    hostname: "server"
    username: "admin"
    password: "pass"
    name: "{{ inventory_hostname }}"
    state: present
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
        "pollinterval": 120,
        "rediscoveryinterval": 30,
        "statcollection": 15,
        "status": 1,
        "statusdescription": "Node status is Up.",
        "unmanaged": false,
        "unmanagefrom": "1899-12-30T00:00:00+00:00",
        "unmanageuntil": "1899-12-30T00:00:00+00:00",
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
    raise


def main():
    argument_spec = orion_argument_spec()
    argument_spec.update(
        state=dict(required=True, choices=['present', 'absent']),
    )
    module = AnsibleModule(
        argument_spec,
        required_one_of=[('name', 'node_id', 'ip_address')],
        supports_check_mode=True,
    )

    orion = OrionModule(module)
    node = orion.get_node()
    if not node:
        module.fail_json(skipped=True, msg='Node not found')
    changed = False

    try:
        ai_polling = orion.swis_query("SELECT Enabled FROM Orion.AssetInventory.Polling WHERE NodeID = '{0}'".format(node['nodeid']))
        if module.params['state'] == 'present':
            if not ai_polling:
                if not module.check_mode:
                    orion.manage_asset_inventory([node['nodeid']], True)
                changed = True
        elif module.params['state'] == 'absent':
            if ai_polling:
                if not module.check_mode:
                    orion.manage_asset_inventory([node['nodeid']], False)
                changed = True
    except Exception as e:
        module.fail_json(msg=str(e))

    module.exit_json(changed=changed, orion_node=node)


if __name__ == '__main__':
    main()
