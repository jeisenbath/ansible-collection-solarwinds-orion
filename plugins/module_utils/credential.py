# -*- coding: utf-8 -*-

# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

def get_credentials(orion, name):
    credential = {}
    query = f"""
    SELECT ID, Name, CredentialType
    FROM Orion.Credential
    WHERE Name = '{name}'
    """
    results = orion.swis.query(query)
    if results['results']:
        credential['ID'] = results['results'][0]['ID']
        credential['Name'] = results['results'][0]['Name']
        credential['CredentialType'] = results['results'][0]['CredentialType']
    return credential

def create_snmpv3_credentials(orion, name, snmp3_props: dict, context: str = '', owner: str = 'Orion'):
    result = orion.swis.invoke(
        'Orion.Credential', 'CreateSNMPv3Credentials', name, snmp3_props['username'], context,
        snmp3_props['auth_method'], snmp3_props['auth_key'], snmp3_props['auth_key_is_pwd'],
        snmp3_props['priv_method'], snmp3_props['priv_key'], snmp3_props['priv_key_is_pwd'],
        owner)
    return result

def create_username_password_credentials(orion, name, wmiProps: dict, owner):
    result = orion.swis.invoke('Orion.Credential', 'CreateUsernamePasswordCredentials', name, wmiProps['username'], wmiProps['password'], owner)
    return result

def validate_snmp3_credentials(orion, node, properties, port: int = 161):
    snmp3_credentials = {
        'UserName': properties['username'],
        'Context': '',
        'PrivacyType': properties['priv_method'],
        'PrivacyPassword': properties['priv_key'],
        'PrivacyKeyIsPassword': properties['priv_key_is_pwd'],
        'AuthenticationPassword': properties['auth_key'],
        'AuthenticationType': properties['auth_method'],
        'AuthenticationKeyIsPassword': properties['auth_key_is_pwd'],
    }
    result = orion.swis.invoke(
        'Orion.Discovery',
        'ValidateCredentials',
        node['ipaddress'],
        port,
        'SolarWinds.Orion.Core.Models.Credentials.SnmpCredentialsV3',
        snmp3_credentials,
        node['engineid'],
    )
    return result

def assign_credentials_to_node(orion, node, credentialSet, nodeSetting):
    properties = {
        'NodeID': node['nodeid'],
        'SettingName': nodeSetting,
        'SettingValue': credentialSet['ID']
    }
    result = orion.swis.create(
        'Orion.NodeSettings',
        **properties
    )
    return result
