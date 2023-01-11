# oktawave-cli

Simple CLI application for managing services in [Oktawave](https://oktawave.com/en) Cloud.

## Installation

Use the package manager [pip] (https://pip.pypa.io/en/stable/) to install oktawave-cli.

```bash
pip install oktawave-cli
```

## Configuration

If you haven't already done so, the first thing you need to do is generate access keys for the API client. You can do it on Account Mangagement app [id.oktawave.com](https://id.oktawave.com/core/en/clients). You can find instruction on [Oktawave Knowledge Base](https://oktawave.com/docs/services/api/autoryzacja).

After getting application API Keys, you need to setup oktawave-cli configuration file in $HOME/.oktawave-cli/config.ini location.

### Example

```bash
mkdir ~/.oktawave-cli && touch ~/.oktawave-cli/config.ini
```
Configuration file has ini format.
Example:
```
[default]  # default access data if --account option will be not specified
username = your_username
password = your_password
access_id = your_api_access_id
access_key = your_api_access_key
ocs_project_name = your_ocs_project_name # Optional, but required for ocs subcommands.
[account2]
username = account2_username
password = account2_password
access_id = account2_access_id
access_key = account2_access_key
ocs_project_name = account2_project_name # Optional, but required for ocs subcommands.
[account3]
username = account3_username
password = account3_password
access_id = account3_access_id
access_key = account3_access_key
ocs_project_name = account3_project_name # Optional, but required for ocs subcommands.
```

You can setup as many account as you need and then you can select which one to use with --account option

## Usage examples

Help
```bash
oktawave-cli --help
```

List all OCI
```bash
oktawave-cli oci list
```

```bash
oktawave-cli --help
```

List all OCI for account1
```bash
oktawave-cli --account account1 oci list
```
List all templates
```bash
oktawave-cli oci templates
```
Create new oci
```bash
oktawave-cli oci create --name foobar --template-id 1339 --ssh-key 1337 --type-id 34
```
