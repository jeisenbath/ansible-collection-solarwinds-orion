#!/usr/bin/python
# -*- coding: utf-8 -*-

# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: orion_node_interface_info
short_description: Get info about interfaces on Nodes in Solarwinds Orion NPM
description:
    - Retrieve information about interfaces on a Node in Orion NPM that are currently being monitored.
    - Provides details such as interface name, status, and other relevant attributes.
version_added: "1.0.0"
author: "Andrew Bailey (@Andyjb8)"
extends_documentation_fragment:
    - solarwinds.orion.orion_auth_options
    - solarwinds.orion.orion_node_options
requirements:
    - orionsdk
    - requests
'''

EXAMPLES = r'''
---

- name: Get info about all interfaces on a node
  solarwinds.orion.orion_node_interface_info:
    hostname: "{{ solarwinds_server }}"
    username: "{{ solarwinds_user }}"
    password: "{{ solarwinds_pass }}"
    name: "{{ inventory_hostname }}"
  delegate_to: localhost

'''

RETURN = r'''
orion_node:
    description: Info about an Orion node.
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
interfaces:
    description: List of interfaces currently monitored on the node.
    returned: always
    type: list
    elements: dict
    sample: [
            {
                "Name": "eth0",
                "InterfaceID": 268420,
                "AdminStatus": 1,
                "OperStatus": 1,
                "Speed": 1000000000.0,
                "Type": 6,
                "Status": 1,
                "StatusDescription": "Up"
            },
            {
                "Name": "eth1",
                "InterfaceID": 268421,
                "AdminStatus": 2,
                "OperStatus": 2,
                "Speed": 1000000000.0,
                "Type": 6,
                "Status": 0,
                "StatusDescription": "Unknown"
            }
        ]
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.solarwinds.orion.plugins.module_utils.orion import OrionModule, orion_argument_spec
try:
    import requests
    HAS_REQUESTS = True
    requests.packages.urllib3.disable_warnings()
except ImportError:
    HAS_REQUESTS = False
except Exception:
    raise Exception
try:
    import orionsdk
    from orionsdk import SwisClient
    HAS_ORION = True
except ImportError:
    HAS_ORION = False
except Exception:
    raise Exception


def main():
    argument_spec = orion_argument_spec()
    module = AnsibleModule(
        argument_spec,
        supports_check_mode=True,
        required_one_of=[('name', 'node_id', 'ip_address')],
    )

    if not HAS_ORION:
        module.fail_json(msg='orionsdk required for this module')

    orion = OrionModule(module)

    node = orion.get_node()
    if not node:
        module.fail_json(skipped=True, msg='Node not found')

    interfaces = []
    try:
        interface_query = orion.swis.query(
            "SELECT Caption, Name, InterfaceID, AdminStatus, OperStatus, Speed, Type, Status, StatusDescription "
            "FROM Orion.NPM.Interfaces WHERE NodeID = '{0}'".format(node['nodeid'])
        )
        interfaces = interface_query['results']
    except Exception as e:
        module.fail_json(msg="Failed to retrieve interfaces: {0}".format(str(e)))

    module.exit_json(changed=False, orion_node=node, interfaces=interfaces)


if __name__ == "__main__":
    main()
