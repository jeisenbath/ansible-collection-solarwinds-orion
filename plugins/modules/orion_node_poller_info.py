#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2024, Josh M. Eisenbath <j.m.eisenbath@gmail.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: orion_node_poller_info
short_description: Gets info about pollers assigned to a Node in Solarwinds Orion NPM
description:
    - "Get the Poller Types assigned to a Node in Solarwinds Orion NPM, and if those pollers are enabled."
version_added: "1.3.0"
author: "Josh M. Eisenbath (@jeisenbath)"
extends_documentation_fragment:
    - jeisenbath.solarwinds.orion_auth_options
    - jeisenbath.solarwinds.orion_node_options
requirements:
    - orionsdk
    - requests
'''

EXAMPLES = r'''
---

- name: Get the pollers assigned to a node
  jeisenbath.solarwinds.orion_node_poller_info:
    hostname: "{{ solarwinds_server }}"
    username: "{{ solarwinds_user }}"
    password: "{{ solarwinds_pass }}"
    name: "{{ node_name }}"
  delegate_to: localhost
  register: poller_info

- name: Loop through the pollers and show PollerType and Enabled
  ansible.builtin.debug:
    msg: "{{ item.PollerType }}: {{ item.Enabled }}"
  loop: "{{ poller_info.pollers }}"

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
pollers:
    description: List of pollers assigned to the orion node.
    returned: always
    type: list
    elements: dict
    sample: [
        {
            "Enabled": false,
            "PollerType": "N.ResponseTime.SNMP.Native"
        },
        {
            "Enabled": false,
            "PollerType": "N.Status.SNMP.Native"
        },
        {
            "Enabled": true,
            "PollerType": "N.LoadAverage.SNMP.Linux"
        },
        {
            "Enabled": true,
            "PollerType": "N.Memory.SNMP.NetSnmpReal"
        }
    ]
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


def main():
    argument_spec = orion_argument_spec()
    module = AnsibleModule(
        argument_spec,
        supports_check_mode=True,
        required_one_of=[('name', 'node_id', 'ip_address')],
    )

    orion = OrionModule(module)

    node = orion.get_node()
    if not node:
        module.fail_json(skipped=True, msg='Node not found')

    changed = False
    if node:
        query = """SELECT p.PollerType, p.Enabled
         from Orion.Nodes n left join Orion.Pollers as p on p.NetObjectID = n.NodeId
          where n.NodeId = '{0}'""".format(node['nodeid'])
        pollers = orion.swis_query(query)

    module.exit_json(changed=changed, orion_node=node, pollers=pollers)


if __name__ == "__main__":
    main()
