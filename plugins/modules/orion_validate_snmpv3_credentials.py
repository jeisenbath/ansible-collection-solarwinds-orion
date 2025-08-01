#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2025, Andrew Bailey (@andyjb8)
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: orion_validate_snmpv3_credentials
short_description: Validate SNMPv3 credentials against a target device using SolarWinds Orion
description:
    - "Validates SNMPv3 credentials against a target IP address using the Orion.Discovery ValidateCredentials verb."
    - "This module allows you to test if SNMPv3 credentials will work on a device before applying them."
    - "Returns True if credentials are valid, False otherwise."
version_added: "1.4.0"
author:
    - "Andrew Bailey (@andyjb8)"
options:
    target_ip:
        description:
            - IP address of the target device to validate credentials against
        required: true
        type: str
    snmp_port:
        description:
            - SNMP port number on the target device
        required: false
        type: int
        default: 161
    credential_name:
        description:
            - Name of the SNMPv3 credential set in SolarWinds Orion
            - If not provided, will use the individual credential parameters
        required: false
        type: str
    snmpv3_username:
        description:
            - SNMPv3 username
            - Required if credential_name is not provided
        required: false
        type: str
    snmpv3_context:
        description:
            - SNMPv3 context
        required: false
        type: str
        default: ""
    snmpv3_auth_method:
        description:
            - SNMPv3 authentication method
        choices: [SHA1, MD5, SHA224, SHA256, SHA384, SHA512]
        required: false
        type: str
        default: "SHA1"
    snmpv3_auth_key:
        description:
            - SNMPv3 authentication key/password
        required: false
        type: str
        no_log: true
    auth_key_is_password:
        description:
            - Whether the authentication key is a password (True) or a key (False)
        required: false
        type: bool
        default: true
    snmpv3_priv_method:
        description:
            - SNMPv3 privacy method
        choices: [DES, DES56, AES128, AES192, AES256]
        required: false
        type: str
        default: "AES128"
    snmpv3_priv_key:
        description:
            - SNMPv3 privacy key/password
        required: false
        type: str
        no_log: true
    priv_key_is_password:
        description:
            - Whether the privacy key is a password (True) or a key (False)
        required: false
        type: bool
        default: true
    engine_id:
        description:
            - SNMPv3 engine ID (typically 1 for most devices)
        required: false
        type: int
        default: 1
    preferred_snmp:
        description:
            - Preferred SNMP version
        choices: [SNMP1, SNMP2, SNMP3]
        required: false
        type: str
        default: "SNMP3"
extends_documentation_fragment:
    - solarwinds.orion.orion_auth_options
requirements:
    - orionsdk
    - requests
'''

EXAMPLES = r'''
---
- name: Validate SNMPv3 credentials using existing credential set
  solarwinds.orion.orion_validate_snmpv3_credentials:
    hostname: "{{ solarwinds_server }}"
    username: "{{ solarwinds_user }}"
    password: "{{ solarwinds_password }}"
    target_ip: "192.168.1.100"
    credential_name: "my_snmpv3_creds"
  delegate_to: localhost

- name: Validate SNMPv3 credentials using individual parameters
  solarwinds.orion.orion_validate_snmpv3_credentials:
    hostname: "{{ solarwinds_server }}"
    username: "{{ solarwinds_user }}"
    password: "{{ solarwinds_password }}"
    target_ip: "192.168.1.100"
    snmpv3_username: "snmp_user"
    snmpv3_context: ""
    snmpv3_auth_method: "SHA1"
    snmpv3_auth_key: "auth_password"
    auth_key_is_password: true
    snmpv3_priv_method: "AES128"
    snmpv3_priv_key: "priv_password"
    priv_key_is_password: true
  delegate_to: localhost

- name: Validate credentials with custom port and engine ID
  solarwinds.orion.orion_validate_snmpv3_credentials:
    hostname: "{{ solarwinds_server }}"
    username: "{{ solarwinds_user }}"
    password: "{{ solarwinds_password }}"
    target_ip: "10.0.0.50"
    snmp_port: 1161
    engine_id: 2
    snmpv3_username: "admin_user"
    snmpv3_auth_method: "SHA256"
    snmpv3_auth_key: "strong_auth_pass"
    snmpv3_priv_method: "AES256"
    snmpv3_priv_key: "strong_priv_pass"
  delegate_to: localhost
'''

RETURN = r'''
validation_result:
    description: Result of the credential validation
    returned: always
    type: bool
    sample: true
message:
    description: Descriptive message about the validation result
    returned: always
    type: str
    sample: "SNMPv3 credentials validated successfully"
credential_details:
    description: Details of the credentials that were validated (passwords redacted)
    returned: always
    type: dict
    sample: {
        "username": "snmp_user",
        "context": "",
        "auth_method": "SHA1",
        "priv_method": "AES128",
        "target_ip": "192.168.1.100",
        "snmp_port": 161
    }
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


def get_credential_by_name(orion, credential_name):
    """
    Retrieve SNMPv3 credential details by name from SolarWinds Orion
    """
    try:
        # Query for the credential by name
        query = """
        SELECT 
            c.ID,
            c.Name,
            s.Username,
            s.Context,
            s.AuthenticationMethod,
            s.AuthenticationKey,
            s.AuthenticationKeyIsPassword,
            s.PrivacyMethod,
            s.PrivacyKey,
            s.PrivacyKeyIsPassword
        FROM Orion.Credential c
        LEFT JOIN Orion.SNMPv3Credentials s ON c.ID = s.ID
        WHERE c.Name = '{0}' AND c.CredentialType = 'SolarWinds.Orion.Core.Models.Credentials.SnmpCredentialsV3'
        """.format(credential_name)
        
        results = orion.swis_query(query)
        
        if results and len(results) > 0:
            return results[0]
        else:
            return None
            
    except Exception as e:
        raise Exception("Failed to retrieve credential '{0}': {1}".format(credential_name, str(e)))


def build_credential_details(module_params, credential_data=None):
    """
    Build the credential details dictionary for the ValidateCredentials call
    """
    if credential_data:
        # Use credentials from SolarWinds database
        return {
            "Name": credential_data['Username'],
            "Context": credential_data['Context'] or "",
            "AuthenticationMethod": credential_data['AuthenticationMethod'],
            "AuthenticationKey": credential_data['AuthenticationKey'],
            "AuthenticationKeyIsPassword": credential_data['AuthenticationKeyIsPassword'],
            "PrivacyMethod": credential_data['PrivacyMethod'],
            "PrivacyKey": credential_data['PrivacyKey'],
            "PrivacyKeyIsPassword": credential_data['PrivacyKeyIsPassword']
        }
    else:
        # Use credentials from module parameters
        return {
            "Name": module_params['snmpv3_username'],
            "Context": module_params['snmpv3_context'],
            "AuthenticationMethod": module_params['snmpv3_auth_method'],
            "AuthenticationKey": module_params['snmpv3_auth_key'],
            "AuthenticationKeyIsPassword": module_params['auth_key_is_password'],
            "PrivacyMethod": module_params['snmpv3_priv_method'],
            "PrivacyKey": module_params['snmpv3_priv_key'],
            "PrivacyKeyIsPassword": module_params['priv_key_is_password']
        }


def validate_credentials(orion, target_ip, snmp_port, credential_details, engine_id, preferred_snmp):
    """
    Call the Orion.Discovery ValidateCredentials verb
    """
    try:
        result = orion.swis.invoke(
            'Orion.Discovery', 
            'ValidateCredentials',
            target_ip,
            snmp_port,
            "SolarWinds.Orion.Core.Models.Credentials.SnmpCredentialsV3",
            credential_details,
            engine_id,
            preferred_snmp
        )
        return result
    except Exception as e:
        raise Exception("Failed to validate credentials: {0}".format(str(e)))


def main():
    argument_spec = orion_argument_spec()
    argument_spec.update(
        target_ip=dict(required=True, type='str'),
        snmp_port=dict(required=False, type='int', default=161),
        credential_name=dict(required=False, type='str'),
        snmpv3_username=dict(required=False, type='str'),
        snmpv3_context=dict(required=False, type='str', default=""),
        snmpv3_auth_method=dict(
            required=False, 
            type='str', 
            choices=['SHA1', 'MD5', 'SHA224', 'SHA256', 'SHA384', 'SHA512'],
            default='SHA1'
        ),
        snmpv3_auth_key=dict(required=False, type='str', no_log=True),
        auth_key_is_password=dict(required=False, type='bool', default=True),
        snmpv3_priv_method=dict(
            required=False,
            type='str',
            choices=['DES', 'DES56', 'AES128', 'AES192', 'AES256'],
            default='AES128'
        ),
        snmpv3_priv_key=dict(required=False, type='str', no_log=True),
        priv_key_is_password=dict(required=False, type='bool', default=True),
        engine_id=dict(required=False, type='int', default=1),
        preferred_snmp=dict(
            required=False,
            type='str',
            choices=['SNMP1', 'SNMP2', 'SNMP3'],
            default='SNMP3'
        )
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        mutually_exclusive=[
            ['credential_name', 'snmpv3_username']
        ],
        required_one_of=[
            ['credential_name', 'snmpv3_username']
        ],
        required_if=[
            ['credential_name', None, ['snmpv3_username', 'snmpv3_auth_key']]
        ]
    )

    if not HAS_ORION:
        module.fail_json(msg='orionsdk required for this module')

    if not HAS_REQUESTS:
        module.fail_json(msg='requests required for this module')

    # Initialize Orion connection
    try:
        orion = OrionModule(module)
    except Exception as e:
        module.fail_json(msg='Failed to connect to SolarWinds Orion: {0}'.format(str(e)))

    # Get parameters
    target_ip = module.params['target_ip']
    snmp_port = module.params['snmp_port']
    engine_id = module.params['engine_id']
    preferred_snmp = module.params['preferred_snmp']
    credential_name = module.params['credential_name']

    credential_data = None
    
    # If credential_name is provided, retrieve credentials from SolarWinds
    if credential_name:
        try:
            credential_data = get_credential_by_name(orion, credential_name)
            if not credential_data:
                module.fail_json(msg="Credential '{0}' not found in SolarWinds Orion".format(credential_name))
        except Exception as e:
            module.fail_json(msg="Error retrieving credential '{0}': {1}".format(credential_name, str(e)))

    # Build credential details for validation
    try:
        credential_details = build_credential_details(module.params, credential_data)
    except Exception as e:
        module.fail_json(msg="Error building credential details: {0}".format(str(e)))

    # Check mode - don't actually validate, just return what would happen
    if module.check_mode:
        module.exit_json(
            changed=False,
            validation_result=None,
            message="Check mode: would validate SNMPv3 credentials for {0}".format(target_ip),
            credential_details={
                "username": credential_details.get("Name", ""),
                "context": credential_details.get("Context", ""),
                "auth_method": credential_details.get("AuthenticationMethod", ""),
                "priv_method": credential_details.get("PrivacyMethod", ""),
                "target_ip": target_ip,
                "snmp_port": snmp_port
            }
        )

    # Validate credentials
    try:
        validation_result = validate_credentials(
            orion, 
            target_ip, 
            snmp_port, 
            credential_details, 
            engine_id, 
            preferred_snmp
        )
        
        # Prepare return data (redact sensitive information)
        return_credential_details = {
            "username": credential_details.get("Name", ""),
            "context": credential_details.get("Context", ""),
            "auth_method": credential_details.get("AuthenticationMethod", ""),
            "priv_method": credential_details.get("PrivacyMethod", ""),
            "target_ip": target_ip,
            "snmp_port": snmp_port
        }
        
        if validation_result:
            message = "SNMPv3 credentials validated successfully for {0}".format(target_ip)
        else:
            message = "SNMPv3 credentials validation failed for {0}".format(target_ip)
            
        module.exit_json(
            changed=False,
            validation_result=validation_result,
            message=message,
            credential_details=return_credential_details
        )
        
    except Exception as e:
        module.fail_json(
            msg="Credential validation failed: {0}".format(str(e)),
            target_ip=target_ip,
            snmp_port=snmp_port
        )


if __name__ == '__main__':
    main()
