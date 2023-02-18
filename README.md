# Solarwinds Collection for Ansible
<!-- Add CI and code coverage badges here. Samples included below. -->

<!-- Describe the collection and why a user would want to use it. What does the collection do? -->
Collection for managing Nodes in Solarwinds Orion.

## Tested with Ansible

<!-- List the versions of Ansible the collection has been tested with. Must match what is in galaxy.yml. -->
2.9

2.12.2

2.13.3

## External requirements

```bash
pip install -r requirements.txt
```

### Installing the Collection from Ansible Galaxy

Before using this collection, you need to install it with the Ansible Galaxy command-line tool:
```bash
ansible-galaxy collection install git+https://github.com/jeisenbath/ansible-collection-solarwinds-orion.git
```

You can also include it in a `requirements.yml` file and install it with `ansible-galaxy collection install -r requirements.yml`, using the format:
```yaml
---
collections:
  - name: solarwinds.orion
    source: git
    repository: https://github.com/jeisenbath/ansible-collection-solarwinds-orion.git
```

Note that if you install the collection from Ansible Galaxy, it will not be upgraded automatically when you upgrade the `ansible` package. To upgrade the collection to the latest available version, run the following command:
```bash
ansible-galaxy collection install git+https://github.com/jeisenbath/ansible-collection-solarwinds-orion.git --upgrade
```

You can also install a specific version of the collection, for example, if you need to downgrade when something is broken in the latest version (please report an issue in this repository). Use the following syntax to install version `1.0.0`:

```bash
ansible-galaxy collection install git+https://github.com/jeisenbath/ansible-collection-solarwinds-orion.git:==1.0.0
```

See [Ansible Using collections](https://docs.ansible.com/ansible/devel/user_guide/collections_using.html) for more details.

## Licensing

<!-- Include the appropriate license information here and a pointer to the full licensing details. If the collection contains modules migrated from the ansible/ansible repo, you must use the same license that existed in the ansible/ansible repo. See the GNU license example below. -->

GNU General Public License v3.0 or later.

See [LICENSE](https://www.gnu.org/licenses/gpl-3.0.txt) to see the full text.

