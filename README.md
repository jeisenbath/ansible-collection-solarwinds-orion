# Solarwinds Collection for Ansible
<!-- Add CI and code coverage badges here. Samples included below. -->

<!-- Describe the collection and why a user would want to use it. What does the collection do? -->
Collection for managing Nodes in Solarwinds Orion.

## Included Content

<!--start collection content-->
### Modules
| Name                                       | Description                                                 |
|--------------------------------------------|-------------------------------------------------------------|
| jeisenbath.solarwinds.orion_custom_property       | Manage custom properties on Node.                    |
| jeisenbath.solarwinds.orion_node                  | Creates, Removes, Manage, or Mute Node.              |
| jeisenbath.solarwinds.orion_node_application      | Manages APM application templates assigned to Nodes. |
| jeisenbath.solarwinds.orion_node_custom_poller    | Creates/Removes custom pollers on a Node.            |
| jeisenbath.solarwinds.orion_node_hardware_health  | Creates/Removes Hardware Health poller on a Node.    |
| jeisenbath.solarwinds.orion_node_info             | Gets info about a Node.                              |
| jeisenbath.solarwinds.orion_node_interface        | Manage interfaces on Nodes.                          |
| jeisenbath.solarwinds.orion_node_interface_info   | Query info about interfaces on a Node.               |
| jeisenbath.solarwinds.orion_node_poller           | Manage Pollers on Nodes.                             |
| jeisenbath.solarwinds.orion_node_poller_info      | Query info about pollers assigned to a Node.         |
| jeisenbath.solarwinds.orion_update_node           | Updates Node properties.                             |
| jeisenbath.solarwinds.orion_volume                | Manage Volumes on Nodes.                             |
| jeisenbath.solarwinds.orion_volume_info           | Gets info about a Volume assigned to a Node.         |
| jeisenbath.solarwinds.orion_node_ncm              | Adds or Removes an existing node to NCM.             |
| jeisenbath.solarwinds.orion_query                 | Run a SWQL query against the orion database.         |

### Plugins
| Name                                   | Description                                   |
|----------------------------------------|-----------------------------------------------|
| jeisenbath.solarwinds.orion_nodes_inventory | Dynamic Inventory Plugin for Solarwinds Orion |

### Roles
| Name                        | Description                    |
|-----------------------------|--------------------------------|
| jeisenbath.solarwinds.orion_node | Add a node to solarwinds orion |

## Tested with Ansible

<!-- List the versions of Ansible the collection has been tested with. Must match what is in galaxy.yml. -->
2.9
2.12.2
2.13.3
2.14.2

## External requirements

```bash
pip install -r requirements.txt
```

### Installing the Collection from Ansible Galaxy

Before using this collection, you need to install it with the Ansible Galaxy command-line tool:
```bash
ansible-galaxy collection install jeisenbath.solarwinds
```

You can also include it in a `requirements.yml` file and install it with `ansible-galaxy collection install -r requirements.yml`, using the format:
```yaml
---
collections:
  - name: jeisenbath.solarwinds
```

Note that if you install the collection from Ansible Galaxy, it will not be upgraded automatically when you upgrade the `ansible` package. To upgrade the collection to the latest available version, run the following command:
```bash
ansible-galaxy collection install jeisenbath.solarwinds --upgrade
```

You can also install a specific version of the collection, for example, if you need to downgrade when something is broken in the latest version (please report an issue in this repository). Use the following syntax to install version `1.0.0`:

```bash
ansible-galaxy collection install jeisenbath.solarwinds,v3.0.0
```

If you are using a version prior to 3.0.0 when the namespace changed from solarwinds.orion to jeisenbath.solarwinds, use this to force update from the stable-2.x branch.
This branch will be maintained with bugfixes until 2026-01-01

```bash
ansible-galaxy collection install git+https://github.com/jeisenbath/ansible-collection-solarwinds-orion.git,stable-2.x --force
```

See [Ansible Using collections](https://docs.ansible.com/ansible/devel/user_guide/collections_using.html) for more details.

## Licensing

<!-- Include the appropriate license information here and a pointer to the full licensing details. If the collection contains modules migrated from the ansible/ansible repo, you must use the same license that existed in the ansible/ansible repo. See the GNU license example below. -->

GNU General Public License v3.0 or later.

See [LICENSE](https://www.gnu.org/licenses/gpl-3.0.txt) to see the full text.

## Community Code of Conduct

Please see the official [Ansible Community Code of Conduct](https://docs.ansible.com/ansible/latest/community/code_of_conduct.html#code-of-conduct).
