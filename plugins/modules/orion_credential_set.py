#!/usr/bin/python
# -*- coding: utf-8 -*-

# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: orion_credential_set
short_description: Manage Credential Sets for Solarwinds.
description:
    - Create Credential Sets in in Solarwinds Credential Set library.
    - Currently the SWIS API does not support removing credential sets.
    - Also can validate and assign credentials to a node.
    - Credentials sets must be created before assigned.
version_added: "3.1.0"
author: "Josh M. Eisenbath (@jeisenbath)"
options:
    state:
        description:
            - Desired state of the credential set.
        required: True
        type: str
        choices:
            - present
            - assigned
    type:
        description:
            - Credential type.
        required: True
        type: str
        choices:
            - snmpv3
            - wmi
    credential_name:
        description:
            - Name of the credential set.
        required: True
        type: str
    snmpv3:
        description:
            - Properties of the credentials.
            - Required to create and verify credentials when assigned when I(type=snmpv3).
        required: False
        type: dict
        suboptions:
            username:
                description:
                    - SNMPv3 username.
                type: str
                required: True
            auth_method:
                description: SNMPv3 Authentication Method
                type: str
                required: False
                choices: ['MD5', 'SHA1', 'SHA256', 'SHA512']
                default: 'SHA1'
            auth_key:
                description: SNMPv3 Authentication Key
                type: str
                required: True
            auth_key_is_pwd:
                description: Whether or not SNMPv3 Authentication is password.
                type: bool
                required: False
                default: True
            priv_key:
                description: SNMPv3 Private Key
                type: str
                required: True
            priv_method:
                description: SNMPv3 Private Key Method
                type: str
                required: False
                choices: ['DES56', 'AES128', 'AES192', 'AES256']
                default: 'DES56'
            priv_key_is_pwd:
                description: Whether or not SNMPv3 Authentication is password.
                type: bool
                required: False
                default: True
            owner:
                description: Credential set owner.
                type: str
                required: False
                default: 'Orion'
    wmi:
        description:
            - WMI credential properties.
            - Required to create and verify credentials when assigned when I(type=wmi).
        required: False
        type: dict
        suboptions:
            username:
                description:
                    - WMI username.
                type: str
                required: True
            password:
                description:
                    - WMI password.
                type: str
                required: True
            owner:
                description: Credential set owner.
                type: str
                required: False
                default: 'Orion'
extends_documentation_fragment:
    - jeisenbath.solarwinds.orion_auth_options
    - jeisenbath.solarwinds.orion_node_options
requirements:
    - orionsdk
    - requests
'''

EXAMPLES = r'''
- name: Create SNMPv3 credential set
  jeisenbath.solarwinds.orion_credential_set:
    hostname: "{{ solarwinds_server }}"
    username: "{{ solarwinds_username }}"
    password: "{{ solarwinds_password }}"
    state: present
    type: snmpv3
    credential_name: "{{ snmpv3_credential_set_name }}"
    snmpv3:
      username: "{{ snmpv3_username }}"
      auth_key: "{{ snmpv3_auth_key }}"
      priv_key: "{{ snmpv3_priv_key }}"
  delegate_to: localhost

- name: Validate and assign Credential Set on an existing node
  jeisenbath.solarwinds.orion_credential_set:
    hostname: "{{ solarwinds_server }}"
    username: "{{ solarwinds_username }}"
    password: "{{ solarwinds_password }}"
    state: assigned
    type: snmpv3
    snmpv3:
      username: "{{ snmpv3_username }}"
      auth_key: "{{ snmpv3_auth_key }}"
      priv_key: "{{ snmpv3_priv_key }}"
    credential_name: "{{ snmpv3_credential_set }}"
    ip_address: "{{ node_ip_address }}"
  delegate_to: localhost

'''

RETURN = r'''
credential:
    description: Info about the credential set from Orion.Credential table.
    returned: always
    type: dict
    sample: {
        "CredentialType": "SolarWinds.Orion.Core.Models.Credentials.SnmpCredentialsV3",
        "ID": 1,
        "Name": "CredentialSetName"
    }
orion_node:
    description: Info about an orion node.
    returned: When I(state=assigned)
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
        "unmanagefrom": "1899-12-30T00:00:00+00:00",
        "unmanageuntil": "1899-12-30T00:00:00+00:00",
        "uri": "swis://host.domain.com/Orion/Orion.Nodes/NodeID=12345"
    }
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.jeisenbath.solarwinds.plugins.module_utils.orion import OrionModule, orion_argument_spec
from ansible_collections.jeisenbath.solarwinds.plugins.module_utils.credential import (
    get_credentials,
    create_snmpv3_credentials,
    create_username_password_credentials,
    validate_snmp3_credentials,
    assign_credentials_to_node
)
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
    argument_spec.update(
        state=dict(required=True, choices=['present', 'assigned']),
        type=dict(required=True, choices=['snmpv3', 'wmi']),
        credential_name=dict(required=True, type='str'),
        snmpv3=dict(required=False, type='dict',
                    options=dict(
                        username=dict(required=True, type='str'),
                        auth_key=dict(required=True, type='str', no_log=True),
                        auth_method=dict(required=False, type='str', choices=['MD5', 'SHA1', 'SHA256', 'SHA512'], default='SHA1'),
                        auth_key_is_pwd=dict(required=False, type='bool', default=True, no_log=False),
                        priv_key=dict(required=True, type='str', no_log=True),
                        priv_method=dict(required=False, type='str', choices=['DES56', 'AES128', 'AES192', 'AES256'], default='DES56'),
                        priv_key_is_pwd=dict(required=False, type='bool', default=True, no_log=False),
                        owner=dict(required=False, type='str', default='Orion'),
                    )),
        wmi=dict(required=False, type='dict',
                 options=dict(
                     username=dict(required=True, type='str'),
                     password=dict(required=True, type='str', no_log=True),
                     owner=dict(required=False, type='str', default='Orion'),
                 )),
    )
    module = AnsibleModule(
        argument_spec,
        supports_check_mode=True,
        required_if=[
            ('type', 'snmpv3', ['snmpv3']),
            ('type', 'wmi', ['wmi']),
            ('state', 'assigned', ['name', 'ip_address', 'node_id'], True)
        ],
    )

    orion = OrionModule(module)

    credential_set = get_credentials(orion, module.params['credential_name'])

    if module.params['state'] == 'assigned':
        node = orion.get_node()
        if not node:
            module.fail_json(skipped=True, msg='Node not found')

    changed = False
    if module.params['state'] == 'present':
        try:
            if not credential_set:
                if not module.check_mode:
                    if module.params['type'] == 'snmpv3':
                        credential_set = create_snmpv3_credentials(orion, module.params['credential_name'], module.params['snmpv3'])
                    elif module.params['type'] == 'wmi':
                        credential_set = create_username_password_credentials(orion, module.params['credential_name'], module.params['wmi'])
                changed = True
        except Exception as OrionException:
            module.fail_json(msg='Failed to create Credential Set: {0}'.format(OrionException))

    if module.params['state'] == 'assigned':
        try:
            if module.params['type'] == 'snmpv3':
                nodeSettingName = 'ROSNMPCredentialID'
                validated = validate_snmp3_credentials(orion, node, module.params['snmpv3'])
                if not validated:
                    module.fail_json(msg='Failed to validate credentials on node.')
            elif module.params['type'] == 'wmi':
                nodeSettingName = 'WMICredential'
            assigned_cred = orion.swis_query(
                "SELECT SettingValue FROM Orion.NodeSettings WHERE NodeID = '{0}' and SettingName = '{1}'".format(node['nodeid'], nodeSettingName)
            )
            if not assigned_cred:
                if not module.check_mode:
                    assign_credentials_to_node(orion, node, credential_set, nodeSettingName)
                changed = True
            elif str(assigned_cred[0]['SettingValue']) != str(credential_set['ID']):
                if not module.check_mode:
                    assign_credentials_to_node(orion, node, credential_set, nodeSettingName)
                changed = True
            module.exit_json(changed=changed, credential=credential_set, orion_node=node)
        except Exception as OrionException:
            module.fail_json(msg='Failed to assign credentials to node: {0}'.format(OrionException))

    module.exit_json(changed=changed, credential=credential_set)


if __name__ == "__main__":
    main()
