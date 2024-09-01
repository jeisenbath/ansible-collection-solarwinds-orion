#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2022, Josh M. Eisenbath <j.m.eisenbath@gmail.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: orion_node_info
short_description: Gets info about a Node in Solarwinds Orion NPM
description:
    - "Get info about a Node in Solarwinds Orion NPM."
version_added: "1.0.0"
author: "Josh M. Eisenbath (@jeisenbath)"
extends_documentation_fragment:
    - solarwinds.orion.orion_auth_options
    - solarwinds.orion.orion_node_options
requirements:
    - orionsdk
    - requests
'''

EXAMPLES = r'''
---

- name: Get info about a node by name
  solarwinds.orion.orion_node_info:
    hostname: "{{ solarwinds_server }}"
    username: "{{ solarwinds_user }}"
    password: "{{ solarwinds_pass }}"
    name: "{{ node_name }}"
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

from datetime import datetime
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.solarwinds.orion.plugins.module_utils.orion import OrionModule, orion_argument_spec
try:
    from dateutil import parser
    HAS_DATEUTIL = True
except ImportError:
    HAS_DATEUTIL = False
except Exception:
    raise Exception
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
    argument_spec = orion_argument_spec
    module = AnsibleModule(
        argument_spec,
        supports_check_mode=True,
        required_one_of=[('name', 'node_id', 'ip_address')],
    )

    orion = OrionModule(module)
    changed = False

    node = orion.get_node()
    if not node:
        module.fail_json(skipped=True, msg='Node not found')

    # trigger poll if last poll is null or greater than 5 minutes ago
    object_subtype = node['objectsubtype']
    if object_subtype == 'SNMP':
        last_poll = node['lastsystemuptimepollutc']
        if not last_poll:
            orion.poll_now(node)
            node = orion.get_node()
        elif last_poll:
            time_since_poll = parser.parse(last_poll).replace(tzinfo=None) - datetime.utcnow()
            if time_since_poll.seconds > 300:
                orion.poll_now(node)
                node = orion.get_node()

    module.exit_json(changed=changed, orion_node=node)


if __name__ == "__main__":
    main()
