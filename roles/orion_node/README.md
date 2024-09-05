orion_node
=========

Adds an node to be monitored in Solarwinds.

Requirements
------------

solarwinds.orion collection

Role Variables
--------------

defaults/main.yml
```yaml
orion_node_solarwinds_server: "{{ solarwinds_server }}"
orion_node_solarwinds_username: "{{ solarwinds_username }}"
orion_node_solarwinds_password: "{{ solarwinds_password }}"
orion_node_caption_name: "{{ ansible_facts.nodename }}"
orion_node_ip_address: "{{ ansible_facts.default_ipv4.address }}"
orion_node_polling_method: ICMP
orion_node_snmp_pollers:
  - name: N.Cpu.SNMP.HrProcessorLoad
    enabled: true
  - name: N.Memory.SNMP.NetSnmpReal
    enabled: true
orion_node_discover_interfaces: false
orion_node_ncm: false
orion_node_snmp_port: 161
orion_node_snmp_allow_64: true
```

Variables required depending on the values of defaults
```yaml
# required when orion_node_polling method is SNMP, set which version of SNMP (choices: 2, 3)
orion_node_snmp_version:
# required when SNMP version is 2
orion_node_ro_community_string:
# required when SNMP version is 3
orion_node_snmpv3_credential_set:
orion_node_snmpv3_username:
orion_node_snmpv3_auth_key:
orion_node_snmpv3_priv_key:

```

Optional variables, define these if you need to configure
```yaml
orion_node_custom_pollers: list, additional custom UnDP pollers
orion_node_interfaces: list, interfaces to monitor
orion_node_volumes: list, volumes to monitor
orion_node_applications: list, APM templates to add to node
orion_node_custom_properties: list, elements are dicts (name, value), custom property names and values to set
orion_node_hardware_health_poller: string, Name of the Hardware Health poller to enable on node
```


Example Playbook
----------------

```yaml

    - name: Add servers to Solarwinds as SNMPv2 nodes
      hosts: servers
      gather_facts: true
      vars:
        solarwinds_server: 127.0.0.1
        solarwinds_username: admin
        solarwinds_password: changeme2345
      roles:
        - role: solarwinds.orion.orion_node
          orion_node_polling_method: SNMP
          orion_node_snmp_version: 2
          orion_node_ro_community_string: community
          orion_node_discover_interfaces: true

```

License
-------

GPL-3.0-or-later
