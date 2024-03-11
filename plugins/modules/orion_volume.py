#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2022, Josh M. Eisenbath <j.m.eisenbath@gmail.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: orion_volume
short_description: Manage Volumes on Nodes in Solarwinds Orion NPM
description:
    - Add or remove a volumes on a node in Orion NPM.
    - This module does not use discovery to find available volumes.
version_added: "1.0.0"
author: "Josh M. Eisenbath (@jeisenbath)"
options:
    state:
        description:
            - The desired state of the volume.
        required: True
        type: str
        choices:
            - present
            - absent
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
                required: True
                type: str
            volumeDescription:
                description:
                    - Description of the volume.
                    - If not given, this will default to name.
                type: str
            volumeType:
                description:
                    - Type of volume.
                choices: [ 'Fixed Disk', 'RAM', 'Virtual Memory', 'Other' ]
                default: 'Fixed Disk'
                type: str
            volumeIcon:
                description:
                    - Volume icon file.
                    - Generally this should match volume type, but with no spaces and file extension at the end.
                default: 'FixedDisk.gif'
                type: str
            pollInterval:
                description:
                    - Time in seconds between polling.
                type: int
                default: 420
            statCollection:
                description:
                    - Time in seconds between stat collection.
                type: int
                default: 15
            rediscoveryInterval:
                description:
                    - Time in seconds between rediscovery.
                type: int
                default: 60
extends_documentation_fragment:
    - solarwinds.orion.orion_auth_options
    - solarwinds.orion.orion_node_options
requirements:
    - orionsdk
    - requests
'''

EXAMPLES = r'''
---

- name: Add /home volume to Linux node
  solarwinds.orion.orion_volume:
    hostname: "{{ solarwinds_server }}"
    username: "{{ solarwinds_user }}"
    password: "{{ solarwinds_pass }}"
    name: "{{ node_name }}"
    state: present
    volume:
      name: /home
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
        state=dict(required=True, choices=['present', 'absent']),
        volume=dict(
            required=True, type='dict',
            options=dict(
                volumeType=dict(
                    type='str', default='Fixed Disk', choices=['Other', 'RAM', 'Virtual Memory', 'Fixed Disk']
                ),
                volumeIcon=dict(type='str', default='FixedDisk.gif'),
                name=dict(required=True, type='str', aliases=['caption']),
                volumeDescription=dict(type='str'),
                pollInterval=dict(type='int', default=420),
                statCollection=dict(type='int', default=15),
                rediscoveryInterval=dict(type='int', default=60),
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
        module.fail_json(skipped=True, msg='Node not found')

    volume = orion.get_volume(node, module.params['volume'])

    if module.params['state'] == 'present':
        if volume:
            module.exit_json(changed=False, orion_node=node, orion_volume=volume)
        else:
            try:
                if module.check_mode:
                    module.exit_json(changed=True, orion_node=node, orion_volume=volume)
                else:
                    orion.add_volume(node, module.params['volume'])
                    volume = orion.get_volume(node, module.params['volume'])
                    orion.add_poller('V', str(volume['volumeid']), 'V.Status.SNMP.Generic', True)
                    orion.add_poller('V', str(volume['volumeid']), 'V.Details.SNMP.Generic', True)
                    orion.add_poller('V', str(volume['volumeid']), 'V.Statistics.SNMP.Generic', True)
                    module.exit_json(changed=True, orion_node=node, orion_volume=volume)
            except Exception as OrionException:
                module.fail_json(msg='Failed to add volume: {0}'.format(str(OrionException)))
    elif module.params['state'] == 'absent':
        if not volume:
            module.exit_json(changed=False, orion_node=node, orion_volume=volume)
        else:
            try:
                if module.check_mode:
                    module.exit_json(changed=True, orion_node=node, orion_volume=volume)
                else:
                    orion.remove_volume(node, module.params['volume'])
                    module.exit_json(changed=True, orion_node=node, orion_volume=volume)
            except Exception as OrionException:
                module.fail_json(msg='Failed to remove volume: {0}'.format(str(OrionException)))
    else:
        module.exit_json(changed=False)


if __name__ == "__main__":
    main()
