import typer
import pyodk
import logging
from pyodk.rest import ApiException
import configparser
import sys
import click
import time
import progressbar
import subprocess
from oktawave_cli.lib.oci import OciHelper
from oktawave_cli.lib.account import AccountHelper
from oktawave_cli.common import Api
from oktawave_cli.utils import pretty_print_output, show_progress_from_ticket, pretty_print_rows

logger = logging.getLogger(__name__)

pass_api = click.make_pass_decorator(Api, ensure=True)

@click.group()
def account():
    """ Manage Account """

@account.command("detail")
@pass_api
def cli_account_detail(api):
    account_instance = AccountHelper(api.api_client)
    account_detail = account_instance.get_account_detail()
    rows = {"Id": "id"}
    pretty_print_rows(rows, account_detail)

@account.group()
@pass_api
def ssh_keys(api):
    pass

@ssh_keys.command("list")
@pass_api
def cli_account_ssh_list(api):
    account_instance = AccountHelper(api.api_client)
    ssh_keys = account_instance.get_ssh_keys()
    output = []
    columns = ["Id", "Name", "Owner User Login", "Creation Date"]
    if ssh_keys:
        for key in ssh_keys.items:
            key_data = [key.id, key.name, key.owner_user.login, key.creation_date]
            output.append(key_data)
    pretty_print_output(columns, output)

@ssh_keys.command("get")
@click.option("--ssh-key-id", required=True, type=int, help="Id of ssh_key")
@pass_api
def cli_account_ssh_get(api, ssh_key_id):
    account_instance = AccountHelper(api.api_client)
    ssh_key = account_instance.get_ssh_key(ssh_key_id)
    output = []
    rows = {"Id": "id",
            "Name": "name",
            "Public Key": "value",
            "Creation Date": "creation_date"}
    pretty_print_rows(rows, ssh_key)

@ssh_keys.command("delete")
@click.option("--ssh-key-id", required=True, type=int, help="Id of ssh_key")
@pass_api
def cli_account_ssh_delete(api, ssh_key_id):
    account_instance = AccountHelper(api.api_client)
    if account_instance.delete_ssh_key(ssh_key_id):
        click.echo("Ssh kye deleted")
    else:
        click.echo("Failed to delete ssh key")
