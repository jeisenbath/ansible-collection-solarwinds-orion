#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2025, Andrew Bailey
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: orion_ncm_config
short_description: Manage device configurations with SolarWinds NCM
description:
    - Manages device configurations in SolarWinds Network Configuration Manager (NCM).
    - Supports importing configurations, uploading to devices, and downloading from devices.
    - The target node must already exist in SolarWinds Orion and be managed by NCM.
    - Uses NCM APIs (ImportConfig, UploadConfig, DownloadConfig) for configuration management.
version_added: "1.4.0"
author: "Andrew Bailey (@Andyjb8)"
options:
    config_content:
        description:
            - The configuration content to import into NCM.
            - This should be the full device configuration as a string.
            - Required for 'import' and 'upload' methods, not used for 'download' method.
        required: false
        type: str
    config_type:
        description:
            - The type of configuration being imported or downloaded.
            - Common values include 'Running', 'Startup', 'Manual', etc.
            - For device-specific types, consult your NCM documentation.
        required: false
        type: str
        default: 'Manual'
    method:
        description:
            - Method to use for configuration operations.
            - 'import' - Import configuration into NCM archive for historical purposes.
            - 'upload' - Upload configuration to the device (if supported).
            - 'download' - Download current configuration from the device into NCM archive.
        required: false
        type: str
        choices: ['import', 'upload', 'download']
        default: 'import'
extends_documentation_fragment:
    - jeisenbath.solarwinds.orion_auth_options
    - jeisenbath.solarwinds.orion_node_options
requirements:
    - orionsdk
    - requests
'''

EXAMPLES = r'''
---

- name: Import device configuration into NCM
  jeisenbath.solarwinds.orion_ncm_config:
    hostname: "{{ solarwinds_server }}"
    username: "{{ solarwinds_user }}"
    password: "{{ solarwinds_pass }}"
    name: "{{ node_name }}"
    config_content: "{{ device_config_backup_content }}"
    config_type: "Running"
    method: import
  delegate_to: localhost

- name: Upload configuration to device via NCM
  jeisenbath.solarwinds.orion_ncm_config:
    hostname: "{{ solarwinds_server }}"
    username: "{{ solarwinds_user }}"
    password: "{{ solarwinds_pass }}"
    name: "{{ node_name }}"
    config_content: "{{ new_device_config }}"
    method: upload
  delegate_to: localhost

- name: Download current configuration from device
  jeisenbath.solarwinds.orion_ncm_config:
    hostname: "{{ solarwinds_server }}"
    username: "{{ solarwinds_user }}"
    password: "{{ solarwinds_pass }}"
    name: "{{ node_name }}"
    config_type: "Running"
    method: download
  delegate_to: localhost

'''

RETURN = r'''
orion_node:
    description: Info about the target orion node.
    returned: always
    type: dict
    sample: {
        "caption": "CORE-SW-01",
        "ipaddress": "192.168.1.100",
        "lastsystemuptimepollutc": "2025-08-28T14:30:12.3600000Z",
        "netobjectid": "N:1234",
        "nodeid": 1234,
        "objectsubtype": "SNMP",
        "status": 1,
        "statusdescription": "Node status is Up.",
        "unmanaged": false,
        "unmanagefrom": "1899-12-30T00:00:00+00:00",
        "unmanageuntil": "1899-12-30T00:00:00+00:00",
        "uri": "swis://orion.example.com/Orion/Orion.Nodes/NodeID=1234"
    }
ncm_result:
    description: Results of the NCM configuration import/upload operation.
    returned: always
    type: dict
    sample: {
        "success": true,
        "node_id": "12345678-abcd-ef01-2345-6789abcdef01",
        "result": null,
        "method": "ImportConfig",
        "parameters_used": {
            "node_id": "12345678-abcd-ef01-2345-6789abcdef01",
            "config_type": "Cisco",
            "title": "daily-backup",
            "comments": "Daily configuration backup import",
            "config_length": 2048
        }
    }
config_history:
    description: Recent configuration history for the node (when method is import).
    returned: when method is import and successful
    type: list
    sample: [
        {
            "ConfigID": "abcd1234-5678-90ef-1234-567890abcdef",
            "NodeID": "12345678-abcd-ef01-2345-6789abcdef01",
            "ConfigType": "Imported",
            "DownloadTime": "2025-08-28T13:16:27.9230000",
            "Description": null,
            "Config": "daily-backup",
            "Comments": "Daily configuration backup import"
        }
    ]
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.jeisenbath.solarwinds.plugins.module_utils.orion import OrionModule, orion_argument_spec
import datetime

try:
    import requests
    HAS_REQUESTS = True
    requests.packages.urllib3.disable_warnings()
except ImportError:
    HAS_REQUESTS = False
except Exception:
    raise Exception


def main():
    # start with generic Orion arguments
    argument_spec = orion_argument_spec()
    # add desired fields to list of module arguments
    argument_spec.update(
        config_content=dict(required=False, type='str', no_log=False),
        config_type=dict(required=False, type='str', default='Manual'),
        method=dict(required=False, choices=['import', 'upload', 'download'], default='import'),
    )
    
    # initialize the custom Ansible module
    module = AnsibleModule(
        argument_spec,
        supports_check_mode=True,
        required_one_of=[('name', 'node_id', 'ip_address')],
    )

    # Validate config_content requirement based on method
    method = module.params['method']
    config_content = module.params['config_content']
    
    if method in ['import', 'upload'] and not config_content:
        module.fail_json(msg=f"config_content is required when method is '{method}'")

    # create an OrionModule object using our custom Ansible module
    orion = OrionModule(module)

    node = orion.get_node()
    if not node:
        # if get_node() returns None, there's no node
        module.fail_json(skipped=True, msg='Node not found')

    # Check if node is managed by NCM
    ncm_node_id = orion.get_ncm_node(node)
    if not ncm_node_id:
        module.fail_json(
            msg='Node is not managed by NCM. Please add the node to NCM first using orion_node_ncm module.'
        )

    config_content = module.params['config_content']
    config_type = module.params['config_type']
    method = module.params['method']

    if module.check_mode:
        check_result = {
            'success': True,
            'node_id': ncm_node_id,
            'method': method,
            'config_type': config_type,
            'check_mode': True
        }
        
        if method == 'download':
            check_result['operation'] = f'Configuration would be downloaded from device {node["caption"]}'
        else:
            check_result['operation'] = f'Configuration would be processed for device {node["caption"]}'
            
        module.exit_json(
            changed=True, 
            orion_node=node, 
            ncm_result=check_result,
            msg="Check mode: no changes made."
        )

    try:
        if method == 'import':
            # Import configuration to NCM archive using ImportConfig verb
            try:
                # Use the exact format from working Python example
                # Parameters: ncm_node_id, config_type, config_text, title, comments
                import uuid
                
                # Ensure NCM NodeID is a proper GUID string
                if isinstance(ncm_node_id, str):
                    try:
                        # Validate and normalize the GUID
                        guid_obj = uuid.UUID(ncm_node_id)
                        normalized_node_id = str(guid_obj)
                    except ValueError:
                        raise Exception(f"Invalid NCM NodeID format: {ncm_node_id}")
                else:
                    normalized_node_id = str(ncm_node_id)
                
                # Prepare parameters exactly like the working Python example
                config_type_str = str(config_type) if config_type else "Running"
                config_text = str(config_content)
                title = "manual-import"
                comments = "Imported via Ansible API"
                
                # Call ImportConfig with the exact parameter order from working example
                result = orion.swis.invoke('Cirrus.ConfigArchive', 'ImportConfig',
                                         normalized_node_id, 
                                         config_type_str, 
                                         config_text,
                                         title,
                                         comments)
                
                import_result = {
                    'success': True, 
                    'result': result, 
                    'node_id': ncm_node_id, 
                    'method': 'ImportConfig',
                    'parameters_used': {
                        'node_id': normalized_node_id,
                        'config_type': config_type_str,
                        'title': title,
                        'comments': comments,
                        'config_length': len(config_text)
                    }
                }
                
                # Get recent configuration history
                config_history = orion.get_ncm_config_history(node, limit=5)
                
                module.exit_json(
                    changed=True,
                    orion_node=node,
                    ncm_result=import_result,
                    config_history=config_history,
                    msg=f'Configuration successfully imported to NCM for node {node["caption"]}'
                )
                
            except Exception as import_error:
                module.fail_json(
                    msg=f'Failed to import configuration to NCM: {str(import_error)}',
                    orion_node=node,
                    ncm_result={
                        'success': False,
                        'error': str(import_error),
                        'node_id': ncm_node_id
                    }
                )

        elif method == 'upload':
            # Upload configuration to device via NCM
            try:
                import uuid
                
                # Ensure NCM NodeID is a proper GUID string
                if isinstance(ncm_node_id, str):
                    try:
                        # Validate and normalize the GUID
                        guid_obj = uuid.UUID(ncm_node_id)
                        normalized_node_id = str(guid_obj)
                    except ValueError:
                        raise Exception(f"Invalid NCM NodeID format: {ncm_node_id}")
                else:
                    normalized_node_id = str(ncm_node_id)
                
                # Prepare parameters for UploadConfig
                config_type_str = str(config_type) if config_type else "Running"
                config_text = str(config_content)
                
                # Call UploadConfig with array of NCM node IDs, config type, content, and boolean flag
                # UploadConfig expects: NodeID[], ConfigType, ConfigContent, ShowProgress (boolean)
                show_progress = True  # Show progress in NCM
                result = orion.swis.invoke('Cirrus.ConfigArchive', 'UploadConfig',
                                         [normalized_node_id],  # Array of node IDs
                                         config_type_str,
                                         config_text,
                                         show_progress)
                
                upload_result = {
                    'success': True, 
                    'result': result, 
                    'node_id': ncm_node_id, 
                    'method': 'UploadConfig',
                    'parameters_used': {
                        'node_id': normalized_node_id,
                        'config_type': config_type_str,
                        'config_length': len(config_text)
                    }
                }
                
                module.exit_json(
                    changed=True,
                    orion_node=node,
                    ncm_result=upload_result,
                    msg=f'Configuration successfully uploaded to device {node["caption"]} via NCM'
                )
                
            except Exception as upload_error:
                module.fail_json(
                    msg=f'Failed to upload configuration to device via NCM: {str(upload_error)}',
                    orion_node=node,
                    ncm_result={
                        'success': False,
                        'error': str(upload_error),
                        'node_id': ncm_node_id,
                        'method': 'UploadConfig'
                    }
                )

        elif method == 'download':
            # Download configuration from device via NCM
            try:
                import uuid
                
                # Ensure NCM NodeID is a proper GUID string
                if isinstance(ncm_node_id, str):
                    try:
                        # Validate and normalize the GUID
                        guid_obj = uuid.UUID(ncm_node_id)
                        normalized_node_id = str(guid_obj)
                    except ValueError:
                        raise Exception(f"Invalid NCM NodeID format: {ncm_node_id}")
                else:
                    normalized_node_id = str(ncm_node_id)
                
                # Prepare config type (default to Running if not specified)
                config_type_str = str(config_type) if config_type else "Running"
                
                # Call DownloadConfig with the NCM node ID and config type
                result = orion.swis.invoke('Cirrus.ConfigArchive', 'DownloadConfig',
                                         [normalized_node_id], 
                                         config_type_str)
                
                download_result = {
                    'success': True, 
                    'result': result, 
                    'node_id': ncm_node_id, 
                    'method': 'DownloadConfig',
                    'parameters_used': {
                        'node_id': normalized_node_id,
                        'config_type': config_type_str,
                        'operation': f'Configuration downloaded from device {node["caption"]}'
                    }
                }
                
                # Get recent configuration history to see the newly downloaded config
                config_history = orion.get_ncm_config_history(node, limit=5)
                
                module.exit_json(
                    changed=True,
                    orion_node=node,
                    ncm_result=download_result,
                    config_history=config_history,
                    msg=f'Configuration successfully downloaded from device {node["caption"]} via NCM'
                )
                
            except Exception as download_error:
                module.fail_json(
                    msg=f'Failed to download configuration from device via NCM: {str(download_error)}',
                    orion_node=node,
                    ncm_result={
                        'success': False,
                        'error': str(download_error),
                        'node_id': ncm_node_id,
                        'method': 'DownloadConfig'
                    }
                )

    except Exception as OrionException:
        module.fail_json(
            msg=f'Failed to process configuration for NCM: {str(OrionException)}',
            orion_node=node
        )

    module.exit_json(changed=False, orion_node=node)


if __name__ == "__main__":
    main()
