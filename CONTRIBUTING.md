# Guidelines for Contributing to Collection

## Building your local development environment

It is highly recommended to set up a python virtual environment for development.
Use the [Ansible Release and Maintenance](https://docs.ansible.com/ansible/latest/reference_appendices/release_and_maintenance.html) to determine the oldest supported python version matching the current minimum ansible version from meta/runtime.yml.  
1. Install the ansible-core version matching the minimum ansible version from meta/runtime.yml.  
2. Install other python package requirements from requirements.txt.  
3. Create a fork of this repository, and clone it to your ansible collection path.
   - Checkout the devel- branch of the current major version.

```
$ mkdir -p ~/.ansible/collections/ansible_collections/solarwinds
$ git clone *your_repo* ~/.ansible/collections/ansible_collections/solarwinds/orion
$ cd ~/.ansible/collections/ansible_collections/solarwinds/orion
$ git checkout devel-2.x
```

### Testing your code

1. Change directory to the collection's root.  
2. Run ansible-test sanity and correct any errors.  
3. Prepare and run integration tests  
    - Copying the test/integration/integration_config_example.yml into integration_config.yml
    - Update the values in integration_config.yml to match your testing environment  
    - If your change includes any files from module_utils, run a full integration test with ansible-test integration.  
    - If you are motifying a single module, or creating a new one, run ansible-test integration *target* to test only that specific resource.  

## Pull requests

### Pre-requisites for new pull requests

All pull requests must:
- Be submitted to the devel branch corresponding to the current major version.  
- Pass an ansible-sanity test.  
- Not include changes to the changelog itself, this will be done by maintainer when merging upstream.  
- Not include changes to galaxy.yml version, nor a build of the collection. This will be done by the maintainer when merging upstream.  

#### Major changes

Major changes include new modules and plugins, or new options for existing ones.  
Major change PRs must:
- Include a changelog fragment with a major_changes section.
- Include an integration test for new modules.
- Include updates to integration test if including new options.
- Only include one new feature per PR.  

Major change PRs should:
- Have either a corresponding open issue or discussion. This is to help ensure some degree of discussion available to all.  

New modules should:
- Import and use OrionModule from module_utils to manage API connection.
- Import and use orion_argument_spec from module_utils, and use corresponding document fragment.
- Include an integration test which tests for:
  - Check mode.
  - Present and absent for state based modules.
  - Updating options for state based modules when state=present.
  - All expected return values for info based modules.
  - Idempotence.

#### Minor changes

Minor changes include new roles or example playbooks, or documentation updates.  
Minor change PRs must:
- Include a changelog fragment with a minor_changes section.  

Minor change PRs should:
- Only create or update one feature per PR.

#### Bugfixes

Bugfix PRs must:
- Include a changelog fragment with a bugfixes section.
- Not include any new features.  

Bugfix PRs should:
- Have a corresponding open issue. This is to help confirm the bug is reproducable and not simply an issue with environment.

## Reporting Issues

General bug reporting guidelines
- Check existing Issues for similar sounding bugs.
- Review ansible-doc documentation and example playbooks when submitting questions. Incomplete, unclear, or inaccurate documentation is an issue!
- Explain your expected behavior versus the actual behavior.
- Include what version of ansible and of the collection you are using. If not using the current version, update and retest.
- Submit a test scenario with the simplest parameters possible to recreate.
