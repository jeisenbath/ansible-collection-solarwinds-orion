#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2022, Josh M. Eisenbath <j.m.eisenbath@gmail.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: orion_volume_info
short_description: Gets info about a Volume in Solarwinds Orion NPM
description:
    - Get info about a Volume in Solarwinds Orion NPM.
version_added: "1.0.0"
author: "Josh M. Eisenbath (@jeisenbath)"
options:
    volume:
        description:
            - Attributes of the volume being managed.
        required: True
        type: dict
        suboptions:
            name:
                description:
                    - Name of the volume.
                aliases: [ 'caption' ]
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

- name: Get info about a volume
  solarwinds.orion.orion_volume_info:
    hostname: "{{ solarwinds_server }}"
    username: "{{ solarwinds_user }}"
    password: "{{ solarwinds_pass }}"
    name: "{{ node_name }}"
    volume:
      name: "{{ volume_name }}"
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
orion_volume:
    description: Info about an orion volume.
    returned: always
    type: dict
    sample: {
        "displayname": "/",
        "volumeindex": 0,
        "status": "0",
        "type": "Fixed Disk",
        "caption": "/",
        "pollinterval": "420",
        "statcollection": "15",
        "rediscoveryinterval": "60",
        "volumedescription": "/",
        "icon": "FixedDisk.gif",
        "uri": "swis://host.domain.com/Orion/Orion.Nodes/NodeID=12345/Volumes/VolumeID=67890"
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
        volume=dict(
            required=True, type='dict',
            options=dict(
                name=dict(type='str', aliases=['caption']),  # TODO required by?
            )
        ),
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
        module.exit_json(skipped=True, msg='Node not found')

    volume = orion.get_volume(node, module.params['volume'])
    if not volume:
        module.exit_json(skipped=True, msg="Volume not found")
    else:
        module.exit_json(changed=False, orion_node=node, orion_volume=volume)


if __name__ == "__main__":
    main()
