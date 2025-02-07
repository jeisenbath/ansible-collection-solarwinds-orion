#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function
__metaclass__ = type

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

DOCUMENTATION = '''
---
module: orion_node_update_snmpv3
short_description: Update SNMPv3 credentials for a node in SolarWinds Orion
version_added: "1.0.0"
description:
    - Update SNMPv3 credentials for an existing node in SolarWinds Orion.
author:
    - "Your Name (@yourhandle)"
options:
    name:
        description:
            - The name of the node in Orion.
        required: true
        type: str
    snmpv3_username:
        description:
            - SNMPv3 username.
        required: false
        type: str
    snmpv3_auth_key:
        description:
            - SNMPv3 authentication key.
        required: false
        type: str
        no_log: true
    snmpv3_auth_method:
        description:
            - SNMPv3 authentication method.
        choices: [SHA1, MD5]
        required: false
        type: str
    snmpv3_priv_key:
        description:
            - SNMPv3 privacy key.
        required: false
        type: str
        no_log: true
    snmpv3_priv_method:
        description:
            - SNMPv3 privacy method.
        choices: [DES56, AES128, AES192, AES256]
        required: false
        type: str
    priv_key_is_password:
        description:
            - Indicates if the privacy key is a password.
        required: false
        type: bool
    auth_key_is_password:
        description:
            - Indicates if the authentication key is a password.
        required: false
        type: bool
    context:
        description:
            - SNMPv3 context.
        required: false
        type: str
requirements:
    - orionsdk
    - requests
''' 

EXAMPLES = '''
- name: Update SNMPv3 credentials
  solarwinds.orion.orion_node_update_snmpv3:
    hostname: "{{ solarwinds_server }}"
    username: "{{ solarwinds_user }}"
    password: "{{ solarwinds_password }}"
    name: "node01"
    snmpv3_username: "snmp_user"
    snmpv3_auth_key: "auth_key"
    snmpv3_auth_method: "SHA1"
    snmpv3_priv_key: "priv_key"
    snmpv3_priv_method: "AES128"
  delegate_to: localhost
'''

RETURN = '''
response:
    description: Details of the updated SNMPv3 credentials.
    type: dict
    returned: always
'''

def main():
    argument_spec = orion_argument_spec()
    argument_spec.update(
        name=dict(required=True, type='str'),
        auth_password=dict(required=False, type='str', no_log=True),
        snmpv3_auth_key=dict(required=False, type='str', no_log=True),
        snmpv3_auth_method=dict(required=False, type='str'),
        context=dict(required=False, type='str'),
        snmpv3_username=dict(required=False, type='str'),
        snmpv3_priv_method=dict(required=False, type='str'),
        snmpv3_priv_key=dict(required=False, type='str', no_log=True),
        priv_key_is_password=dict(required=False, type='bool')
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        required_one_of=[('snmpv3_auth_key', 'snmpv3_auth_method', 'auth_key_is_password', 'context', 'snmpv3_username', 'snmpv3_priv_method', 'snmpv3_priv_key', 'priv_key_is_password')],
    )

    if not HAS_ORION:
        module.fail_json(msg='orionsdk required for this module')

    orion = OrionModule(module)

    returnVals = orion.swis_query(
        """
        SELECT
        n.NodeID,
        n.Caption,
        c.Name,
        c.ID,
        m.Username,
        m.AuthenticationKey,
        m.AuthenticationKeyIsPassword,
        m.AuthenticationMethod,
        m.Context,
        m.PrivacyKey,
        m.PrivacyKeyIsPassword,
        m.PrivacyMethod,
        c.Uri
        FROM Orion.Nodes n
        RIGHT JOIN 
        (SELECT SettingValue, NodeID
        FROM Orion.NodeSettings  
        WHERE SettingValue NOT LIKE '%[^0-9]%') s ON n.NodeID = s.NodeID
        LEFT JOIN Orion.Credential c ON c.ID = s.SettingValue
        LEFT JOIN Orion.SNMPv3Credentials m ON m.NodeID = s.NodeID
        WHERE n.Caption LIKE '%' + '{0}' + '%'
        """.format(module.params['name'])
    )[0]

    credId = returnVals['ID']
    nodeId = returnVals['NodeID']
    name = returnVals['Name']
    snmpUsername = returnVals['Username']
    context = returnVals['Context']
    authenticationMethod = returnVals['AuthenticationMethod']
    authenticationPassword = returnVals['AuthenticationKey']
    authenticationKeyIsPassword = returnVals['AuthenticationKeyIsPassword']
    privacyMethod = returnVals['PrivacyMethod']
    privacyPassword = returnVals['PrivacyKey']
    privacyKeyIsPassword = returnVals['PrivacyKeyIsPassword']

    orion.swis.invoke('Orion.Credential', 'UpdateSNMPv3Credentials',
                      credId,
                      name,
                      snmpUsername,
                      context,
                      authenticationMethod,
                      authenticationPassword,
                      authenticationKeyIsPassword,
                      privacyMethod,
                      privacyPassword,
                      privacyKeyIsPassword)

    module.exit_json(changed=True, response='SNMPv3 credentials updated successfully')

if __name__ == '__main__':
    main()
