import typer
import pyodk
import logging
from pyodk.rest import ApiException
import configparser
import sys
import click
import progressbar
from oktawave_cli.lib.oci import OciHelper
from oktawave_cli.lib.account import AccountHelper
from oktawave_cli.common import Api
from oktawave_cli.utils import pretty_print_output, show_progress_from_ticket, pretty_print_rows

logger = logging.getLogger(__name__)

pass_api = click.make_pass_decorator(Api, ensure=True)

@click.command()
@pass_api
def auth(api):
    """ Gets and prints access token """
    try:
        token = api.token
        click.echo(f"Token {token}")
    except ApiException as err:
        logging.error("Could not get access token ", err)
    except Exception as general_err:
        logging.error("Could not get access token ", general_err)
