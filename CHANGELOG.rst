==============================
Solarwinds.Orion Release Notes
==============================

.. contents:: Topics


v3.1.0
======

Release Summary
---------------

Released TBD

New Modules
-----------

- jeisenbath.solarwinds.orion_credential_set - Manage Credential Sets for Solarwinds.

v3.0.1
======

Release Summary
---------------

Released 2025-01-30

Bugfixes
--------

- orion_node_interface - fixed a bug with adding a defined interface. Check mode was adding the interface, while non-check mode wasn't.

v3.0.0
======

Release Summary
---------------

Released 2025-01-18
Migrated collection to jeisenbath.solarwinds namespace in order to publish to Galaxy.
Versions < 3.0 will stay on old solarwinds.orion namespace, and bugfixes will be ported to stable-2.x branch until 2025-12-31.


Breaking Changes / Porting Guide
--------------------------------

- Bumped min ansible version to be up to date with supported releases. Older versions may work but will no longer be tested.
- Migrated collection namespace from solarwinds.orion to jeisenbath.solarwinds

v2.1.1
======

Release Summary
---------------

Released 2025-01-18
Added ENV variable support for plugins
Created integration tests for modules
Adds a CONTRIBUTING doc
Fix sanity test errors


Minor Changes
-------------

- Add support for Environment Variables for hostname, username, and password

Deprecated Features
-------------------

- Bugfixes will be ported to stable-2.x branch for this collection when applicable to existing plugins until 2026.
- Starting with version 3.0, Collection has been moved to jeisenbath.solarwinds namespace in order to publish to Ansible Galaxy.

v2.1.0
======

Release Summary
---------------

Released 2024-10-02

Major Changes
-------------

- Added module orion_node_interface_info to get interfaces currently monitored for a node.
- Added orion_node_hardware_health module. This module allows for adding and removing hardware health sensors in Solarwinds Orion.

Minor Changes
-------------

- Add a poll_now() function to the OrionModule
- Add a profile_name parameter to orion_node_ncm
- Add correct check_mode logic to orion_ndoe_ncm
- Call poll_now() for SNMP nodes in orion_node_info module. This logic will allow using 'until' task logic to validate node is polling.
- Modified the example playbook for orion_add_node.yml to use the role keyword, and include a task for SNMP poll verification.
- Update get_node() function to also return LastSystemUptimePollUtc
- Updated orion_node module to no longer require snmpv3 credential set.
- Updated orion_update_node exmaples to show updating to SNMPv3.
- orion_node role - added tasks for new modules orion_node_ncm and orion_node_hardware_health

Bugfixes
--------

- Fixed an issue where ansible-lint would complain about missing parameters when a single yaml doc used multiple modules.

v2.0.0
======

Release Summary
---------------

Released 2024-04-18

Breaking Changes / Porting Guide
--------------------------------

- All modules - add support for orionsdk 0.4.0
- If using orionsdk 0.4.0 while still on a version of Solarwinds older than 2024.1.0, must set port to 17778 legacy API
- SWIS API connection parameter for "port" added, with default "17774" to match orionsdk SwisClient default
- SWIS API connection parameter for "verify" added, with default of "false" to match orionsdk SwisClient default

v1.3.2
======

Release Summary
---------------

Released 2024-04-17

Minor Changes
-------------

- inventory plugin orion_nodes_inventory - add ansible vault support for the password parameter

v1.3.1
======

Release Summary
---------------

Released 2024-03-11

Minor Changes
-------------

- orion_node_interface - refactored to try and make as idempotent as possible, and return 'discovered' and 'interface'

v1.3.0
======

Release Summary
---------------

Released 2024-03-07

Major Changes
-------------

- Add module orion_node_ncm - Adds/Removes an existing node to be managed in NCM.
- Add module orion_node_poller_info - Gets pollers assigned to a node and their enabled status.
- Add module orion_query - Runs a SWQL query against Orion database, outputs to json and optional CSV.

New Modules
-----------

- jeisenbath.solarwinds.orion_node_ncm - Manages a node in Solarwinds NCM
- jeisenbath.solarwinds.orion_node_poller_info - Gets info about pollers assigned to a Node in Solarwinds Orion NPM
- jeisenbath.solarwinds.orion_query - Queries the Solarwinds Orion database

v1.2.0
======

Release Summary
---------------

Released 2024-03-01

Major Changes
-------------

- Added a role orion_node
- Updated the example playbook to use the new role

v1.1.0
======

Release Summary
---------------

| Released 2023-12-1


Major Changes
-------------

- Add dynamic inventory plugin jeisenbath.solarwinds.orion_nodes_inventory

v1.0.4
======

Release Summary
---------------

| Released 2023-09-26


Major Changes
-------------

- orion_node_interface module - add param 'regex' to explicitly state if you want to do pattern matching in interface name

Bugfixes
--------

- orion_node module - fix functionality for adding External nodes

v1.0.3
======

Release Summary
---------------

| Released 2023-08-27


Minor Changes
-------------

- orion_node module - add support for using credential sets for SNMPv3 nodes, updated documentation with params that are required for SNMPv3

Bugfixes
--------

- orion.py get_least_used_polling_engine - convert the query count to an int, to fix an issue with a deployment with only one poller

v1.0.2
======

Release Summary
---------------

| Released 2023-08-10


Minor Changes
-------------

- orion_node_interface module - add support for removing all interfaces if one is not specified

Bugfixes
--------

- orion.py add_interface function - only regex pattern match if exact interface name is not found
- orion_node module - don't set snmpv3 properties for node unless parameters are passed
- orion_node_application module - typo with param name 'skip_duplicates'
- orion_node_interface - add to documentation and examples to clarify regex pattern matching is supported

v1.0.1
======

Release Summary
---------------

| Released 2023-07-14


Minor Changes
-------------

- orion_node module - use datetime.now() instead of datetime.utcnow() for muting and unmanaging. utcnow() works fine for managing, but for muting the time needs to match server time to work correctly.

Bugfixes
--------

- orion_node module - add snmp_version required_if polling_method == 'SNMP'
- orion_node module - fix typo in logic for state 'managed'
- orion_node module - unset default for snmp version in parameters, to fix issue 2

v1.0.0
======

Release Summary
---------------

| Released 2023-03-18


New Modules
-----------

- jeisenbath.solarwinds.orion_custom_property - Manage custom properties on Node in Solarwinds Orion NPM
- jeisenbath.solarwinds.orion_node - Created/Removes/Edits Nodes in Solarwinds Orion NPM
- jeisenbath.solarwinds.orion_node_application - Manages APM application templates assigned to nodes.
- jeisenbath.solarwinds.orion_node_custom_poller - Creates/Removes custom pollers to a Node in Solarwinds Orion NPM
- jeisenbath.solarwinds.orion_node_info - Gets info about a Node in Solarwinds Orion NPM
- jeisenbath.solarwinds.orion_node_interface - Manage interfaces on Nodes in Solarwinds Orion NPM
- jeisenbath.solarwinds.orion_node_poller - Manage Pollers on Nodes in Solarwinds Orion NPM
- jeisenbath.solarwinds.orion_update_node - Updates Node in Solarwinds Orion NPM
- jeisenbath.solarwinds.orion_volume - Manage Volumes on Nodes in Solarwinds Orion NPM
- jeisenbath.solarwinds.orion_volume_info - Gets info about a Volume in Solarwinds Orion NPM
