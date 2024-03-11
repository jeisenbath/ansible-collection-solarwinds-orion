#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2022, Josh M. Eisenbath <j.m.eisenbath@gmail.com>
# Copyright: (c) 2019, Jarett D. Chaiken <jdc@salientcg.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = '''
---
module: orion_node
short_description: Created/Removes/Edits Nodes in Solarwinds Orion NPM
description:
    - "Create or Remove Nodes in Orion NPM."
version_added: "1.0.0"
author:
    - "Jarett D Chaiken (@jdchaiken)"
    - "Josh M. Eisenbath (@jeisenbath)"
options:
    state:
        description:
            - The desired state of the node.
        required: true
        type: str
        choices:
            - present
            - absent
            - managed
            - unmanaged
            - muted
            - unmuted
    node_id:
        description:
            - Node ID of the node.
            - One of I(ip_address), I(node_id), or I(name) is required.
        required: false
        type: str
    name:
        description:
            - Name of the node.
            - When I(state=present), this field is required.
            - When state is other than present, one of I(ip_address), I(node_id), or I(name) is required.
        required: false
        aliases: [ 'caption' ]
        type: str
    ip_address:
        description:
            - IP Address of the node.
            - One of I(ip_address), I(node_id), or I(name) is required.
        required: false
        type: str
    unmanage_from:
        description:
            - "The date and time (in ISO 8601 UTC format) to begin the unmanage period."
            - If this is in the past, the node will be unmanaged effective immediately.
            - If not provided, module defaults to now.
            - "ex: 2017-02-21T12:00:00Z"
        required: false
        type: str
    unmanage_until:
        description:
            - "The date and time (in ISO 8601 UTC format) to end the unmanage period."
            - You can set this as far in the future as you like.
            - If not provided, module defaults to 24 hours from now.
            - "ex: 2017-02-21T12:00:00Z"
        required: false
        type: str
    polling_method:
        description:
            - Polling method to use.
        choices:
            - External
            - ICMP
            - SNMP
            - WMI
            - Agent
        default: ICMP
        required: false
        type: str
    ro_community_string:
        description:
            - SNMP Read-Only Community string.
            - Required if I(polling_method=snmp).
        required: false
        type: str
    rw_community_string:
        description:
            - SNMP Read-Write Community string
        required: false
        type: str
    snmp_version:
        description:
            - SNMPv2c or SNMPv3 for snmp polling.
        choices:
            - "2"
            - "3"
        required: false
        type: str
    snmp_port:
        description:
            - Port that SNMP server listens on.
        required: false
        default: "161"
        type: str
    snmp_allow_64:
        description:
            - Set true if device supports 64-bit counters.
        type: bool
        default: true
        required: false
    snmpv3_credential_set:
        description:
            - Credential set name for SNMPv3 credentials.
            - Required when SNMP version is 3.
    snmpv3_username:
        description:
            - Read-Only SNMPv3 username.
            - Required when SNMP version is 3.
        type: str
        required: false
    snmpv3_auth_method:
        description:
            - Authentication method for SNMPv3.
            - Required when SNMP version is 3.
        type: str
        default: SHA1
        choices:
            - SHA1
            - MD5
        required: false
    snmpv3_auth_key:
        description:
            - Authentication passphrase for SNMPv3.
            - Required when SNMP version is 3.
        type: str
        required: false
    snmpv3_auth_key_is_pwd:
        description:
            - SNMPv3 Authentication Password is a key.
            - Confusingly, value of True corresponds to web GUI checkbox being unchecked.
        type: bool
        default: True
        required: false
    snmpv3_priv_method:
        description:
            - Privacy method for SNMPv3.
        type: str
        default: AES128
        choices:
            - DES56
            - AES128
            - AES192
            - AES256
        required: false
    snmpv3_priv_key:
        description:
            - Privacy passphrase for SNMPv3
        type: str
        required: false
    snmpv3_priv_key_is_pwd:
        description:
            - SNMPv3 Privacy Password is a key.
            - Confusingly, value of True corresponds to web GUI checkbox being unchecked.
        type: bool
        default: True
        required: false
    wmi_credential_set:
        description:
            - 'Credential Name already configured in NPM  Found under "Manage Windows Credentials" section of the Orion website (Settings)'
            - "Note: creation of credentials are not supported at this time"
            - Required if I(polling_method=wmi).
        required: false
        type: str
    polling_engine:
        description:
            - ID of polling engine that NPM will use to poll this device.
            - If not passed, will query for the Polling Engine with least nodes assigned.
            - Not recommended to use I(polling_engine=1), which should be the main app server.
        required: false
        type: str
extends_documentation_fragment:
    - solarwinds.orion.orion_auth_options
requirements:
    - orionsdk
    - python-dateutil
    - requests
'''

EXAMPLES = '''
---
- name: Add an SNMP node to Orion
  solarwinds.orion.orion_node:
    hostname: "{{ solarwinds_server }}"
    username: "{{ solarwinds_username }}"
    password: "{{ solarwinds_password }}"
    name: "{{ node_name }}"
    state: present
    ip_address: "{{ node_ip_address }}"
    polling_method: SNMP
    ro_community_string: "{{ snmp_ro_community_string }}"
  delegate_to: localhost

- name: Mute node in Solarwinds for 30 minutes
  solarwinds.orion.orion_node:
    hostname: "{{ solarwinds_host }}"
    username: "{{ solarwinds_username }}"
    password: "{{ solarwinds_password }}"
    state: muted
    ip_address: "{{ ip_address }}"
    unmanage_until: "{{ '%Y-%m-%dT%H:%M:%S' | strftime((now(fmt='%s')|int) + 1800) }}Z"
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

from datetime import datetime, timedelta
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


def add_credential_set(node, credential_set_name, credential_set_type):
    credential_set_type_valid = ['WMICredential', 'ROSNMPCredentialID', 'RWSNMPCredentialID']
    cred_id_query = __SWIS__.query(
        "SELECT ID FROM Orion.Credential WHERE Name = '{0}'".format(credential_set_name)
    )

    credential_id = cred_id_query['results'][0]['ID']
    if credential_id and credential_set_type in credential_set_type_valid:
        nodesettings = {
            'nodeid': node['nodeid'],
            'SettingName': credential_set_type,
            'SettingValue': str(credential_id),
        }
        __SWIS__.create('Orion.NodeSettings', **nodesettings)


def add_node(module, orion):

    props = {
        'IPAddress': module.params['ip_address'],
        'Caption': module.params['name'],
        'ObjectSubType': module.params['polling_method'].upper(),
        'Community': module.params['ro_community_string'],
        'RWCommunity': module.params['rw_community_string'],
        'SNMPVersion': module.params['snmp_version'],
        'AgentPort': module.params['snmp_port'],
        'Allow64BitCounters': module.params['snmp_allow_64'],
        'External': False,
    }

    if module.params['polling_engine']:
        props['EngineID'] = module.params['polling_engine']
    else:
        props['EngineID'] = orion.get_least_used_polling_engine()

    if props['ObjectSubType'] == 'EXTERNAL':
        props['ObjectSubType'] = 'ICMP'

    if module.params['polling_method'].upper() == 'EXTERNAL':
        props['External'] = True

    if module.params['snmp_version'] == '3' and props['ObjectSubType'] == 'SNMP':
        # Even when using credential set, node creation fails without providing all three properties
        props['SNMPV3Username'] = module.params['snmpv3_username']
        props['SNMPV3PrivKey'] = module.params['snmpv3_priv_key']
        props['SNMPV3AuthKey'] = module.params['snmpv3_auth_key']

        # Set defaults here instead of at module level, since we only want for snmpv3 nodes
        if module.params['snmpv3_priv_method']:
            props['SNMPV3PrivMethod'] = module.params['snmpv3_priv_method']
        else:
            props['SNMPV3PrivMethod'] = 'AES128'
        if module.params['snmpv3_priv_key_is_pwd']:
            props['SNMPV3PrivKeyIsPwd'] = module.params['snmpv3_priv_key_is_pwd']
        else:
            props['SNMPV3PrivKeyIsPwd'] = True
        if module.params['snmpv3_auth_method']:
            props['SNMPV3AuthMethod'] = module.params['snmpv3_auth_method']
        else:
            props['SNMPV3AuthMethod'] = 'SHA1'
        if module.params['snmpv3_auth_key_is_pwd']:
            props['SNMPV3AuthKeyIsPwd'] = module.params['snmpv3_auth_key_is_pwd']
        else:
            props['SNMPV3AuthKeyIsPwd'] = True

    # Add Node
    try:
        __SWIS__.create('Orion.Nodes', **props)
    except Exception as OrionException:
        module.fail_json(msg='Failed to create node: {0}'.format(str(OrionException)))

    # Get node after being created
    node = orion.get_node()

    # If we don't use credential sets, each snmpv3 node will create its own credential set
    # TODO option for read/write sets?
    if props['ObjectSubType'] == 'SNMP' and props['SNMPVersion'] == '3':
        add_credential_set(node, module.params['snmpv3_credential_set'], 'ROSNMPCredentialID')

    # If Node is a WMI node, assign credential
    if props['ObjectSubType'] == 'WMI':
        add_credential_set(node, module.params['wmi_credential_set'], 'WMICredential')

    # Add Standard Default Pollers
    icmp_pollers = {
        'N.Status.ICMP.Native': True,
        'N.ResponseTime.ICMP.Native': True,
        'N.IPAddress.ICMP.Generic': True
    }

    snmp_pollers = {
        'N.Status.ICMP.Native': True,
        'N.Status.SNMP.Native': False,
        'N.ResponseTime.ICMP.Native': True,
        'N.ResponseTime.SNMP.Native': False,
        'N.Details.SNMP.Generic': True,
        'N.Uptime.SNMP.Generic': True,
        'N.Routing.SNMP.Ipv4CidrRoutingTable': False,
        'N.Topology_Layer3.SNMP.ipNetToMedia': False,
    }

    if module.params['polling_method'].upper() == 'ICMP':
        pollers_enabled = icmp_pollers
    elif module.params['polling_method'].upper() == 'SNMP':
        pollers_enabled = snmp_pollers
    else:
        pollers_enabled = {}

    for k in pollers_enabled:
        try:
            orion.add_poller('N', str(node['nodeid']), k, pollers_enabled[k])
        except Exception as OrionException:
            module.fail_json(msg='Failed to create pollers on node: {0}'.format(str(OrionException)))

    return node


def remove_node(module, node):
    try:
        __SWIS__.delete(node['uri'])
        module.exit_json(changed=True, orion_node=node)
    except Exception as OrionException:
        module.fail_json(msg='Error removing node: {0}'.format(str(OrionException)))


def remanage_node(module, node):
    if not node['unmanaged']:
        module.exit_json(changed=False, orion_node=node)

    try:
        __SWIS__.invoke('Orion.Nodes', 'Remanage', node['netobjectid'])
        module.exit_json(changed=True, orion_node=node)
    except Exception as OrionException:
        module.fail_json(msg='Error remanaging node: {0}'.format(str(OrionException)))


def unmanage_node(module, node):
    now = datetime.now()
    tomorrow = now + timedelta(days=1)

    unmanage_from = module.params['unmanage_from']
    unmanage_until = module.params['unmanage_until']

    if not unmanage_from:
        unmanage_from = now.isoformat()
    if not unmanage_until:
        unmanage_until = tomorrow.isoformat()

    elif node['unmanaged']:
        module.exit_json(changed=False, orion_node=node)

    try:
        __SWIS__.invoke(
            'Orion.Nodes',
            'Unmanage',
            node['netobjectid'],
            unmanage_from,
            unmanage_until,
            False  # use Absolute Time
        )
        module.exit_json(changed=True, orion_node=node)
    except Exception as OrionException:
        module.fail_json(msg='Error unmanaging node: {0}'.format(str(OrionException)))


def mute_node(module, node):
    now = datetime.now()
    tomorrow = now + timedelta(days=1)

    unmanage_from = module.params['unmanage_from']
    unmanage_until = module.params['unmanage_until']

    if not unmanage_from:
        unmanage_from = now.isoformat()
    if not unmanage_until:
        unmanage_until = tomorrow.isoformat()

    try:
        suppressed_state = __SWIS__.invoke('Orion.AlertSuppression', 'GetAlertSuppressionState', [node['uri']])[0]

        # SuppressionMode 1 is suppressed, 0 unsuppressed
        if suppressed_state['SuppressionMode'] == 0:
            __SWIS__.invoke('Orion.AlertSuppression', 'SuppressAlerts', [node['uri']], unmanage_from, unmanage_until)
            module.exit_json(changed=True, orion_node=node)
        # todo if unmanage_until param > current unmanage until, update time
        else:
            module.exit_json(changed=False, orion_node=node)
    except Exception as OrionException:
        module.fail_json(msg='Error muting node: {0}'.format(str(OrionException)))


def unmute_node(module, node):
    suppressed_state = __SWIS__.invoke('Orion.AlertSuppression', 'GetAlertSuppressionState', [node['uri']])[0]

    try:
        # SuppressionMode 1 is suppressed, 0 unsuppressed
        if suppressed_state['SuppressionMode'] == 0:
            module.exit_json(changed=False, orion_node=node)
        else:
            __SWIS__.invoke('Orion.AlertSuppression', 'ResumeAlerts', [node['uri']])
            module.exit_json(changed=True, orion_node=node)
    except Exception as OrionException:
        module.fail_json(msg='Error muting node: {0}'.format(str(OrionException)))


def main():
    argument_spec = orion_argument_spec
    argument_spec.update(
        state=dict(required=True, choices=['present', 'absent', 'managed', 'unmanaged', 'muted', 'unmuted']),
        unmanage_from=dict(required=False, default=None),
        unmanage_until=dict(required=False, default=None),
        polling_method=dict(required=False, default='ICMP', choices=['External', 'ICMP', 'SNMP', 'WMI', 'Agent']),
        ro_community_string=dict(required=False, no_log=True),
        rw_community_string=dict(required=False, no_log=True),
        snmp_version=dict(required=False, default=None, choices=['2', '3']),
        snmpv3_credential_set=dict(required=False, default=None, type=str),
        snmpv3_username=dict(required=False, type=str),
        snmpv3_auth_method=dict(required=False, type=str, choices=['SHA1', 'MD5']),
        snmpv3_auth_key=dict(required=False, type=str, no_log=True),
        snmpv3_auth_key_is_pwd=dict(required=False, type=bool),
        snmpv3_priv_method=dict(required=False, type=str, choices=['DES56', 'AES128', 'AES192', 'AES256']),
        snmpv3_priv_key=dict(required=False, type=str, no_log=True),
        snmpv3_priv_key_is_pwd=dict(required=False, type=bool),
        snmp_port=dict(required=False, default='161'),
        snmp_allow_64=dict(required=False, default=True, type='bool'),
        wmi_credential_set=dict(required=False, no_log=True),
        polling_engine=dict(required=False),
    )

    module = AnsibleModule(
        argument_spec,
        supports_check_mode=True,
        required_one_of=[('name', 'node_id', 'ip_address')],
        required_if=[
            ('state', 'present', ('name', 'ip_address', 'polling_method')),
            ('snmp_version', '2', ['ro_community_string']),
            ('snmp_version', '3', ['snmpv3_credential_set', 'snmpv3_username', 'snmpv3_auth_key', 'snmpv3_priv_key']),
            ('polling_method', 'SNMP', ['snmp_version']),
            ('polling_method', 'WMI', ['wmi_credential_set']),
        ],
    )

    if not HAS_ORION:
        module.fail_json(msg='orionsdk required for this module')

    options = {
        'hostname': module.params['hostname'],
        'username': module.params['username'],
        'password': module.params['password'],
    }

    global __SWIS__
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

    if module.params['state'] == 'present':
        if node:
            module.exit_json(changed=False, orion_node=node)

        if module.check_mode:
            module.exit_json(changed=True, orion_node=node)
        else:
            new_node = add_node(module, orion)
            module.exit_json(changed=True, orion_node=new_node)
    elif module.params['state'] == 'absent':
        if not node:
            module.exit_json(changed=False)

        if module.check_mode:
            module.exit_json(changed=True, orion_node=node)
        else:
            remove_node(module, node)
    else:
        if not node:
            module.exit_json(skipped=True, msg='Node not found')

        if module.params['state'] == 'managed':
            if module.check_mode:
                module.exit_json(changed=True, orion_node=node)
            else:
                remanage_node(module, node)
        elif module.params['state'] == 'unmanaged':
            if module.check_mode:
                module.exit_json(changed=True, orion_node=node)
            else:
                unmanage_node(module, node)
        elif module.params['state'] == 'muted':
            if module.check_mode:
                module.exit_json(changed=True, orion_node=node)
            else:
                mute_node(module, node)
        elif module.params['state'] == 'unmuted':
            if module.check_mode:
                module.exit_json(changed=True, orion_node=node)
            else:
                unmute_node(module, node)


if __name__ == "__main__":
    main()
