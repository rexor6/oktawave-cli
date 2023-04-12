import click
import click_completion
import logging
from pyodk.rest import ApiException
from .auth.idserver import get_access_token
import os
from .commands.oci import *
from .commands.ocs import *
from .commands.storage import *
from .commands.account import *
from .common import Api

logging.basicConfig(level=logging.INFO,
                    format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
REGION_PL1 = ('PL1', 'PL-1-WAW')
REGION_PL2 = ('PL2', 'PL-2-KRK')

click_completion.init()

@click.group()
@click.version_option()
@click.option('--account', help='Project name to use from config file',
              default='default', required=False)
@click.option('--region', help='Services region: PL1 or PL-1-WAW for WAW (default),PL2 or PL-2-KRK for Krakow', default='PL1')
@click.option('--debug', is_flag=True, help="Set logging level to Debug")
@click.pass_context
def cli(ctx, account, region, debug):
    """Oktawave CLI."""
    ctx.obj = Api(account, region)
    if region.upper() not in REGION_PL1 \
       and region.upper() not in REGION_PL2:
        click.echo("Bad region, enter the correct region")
        sys.exit(-1)
    if debug:
        logger.setLevel(level=logging.DEBUG)


@click.command("install-autocomplete")
@click.option('--append/--overwrite', help="Append the completion code to the file", default=None)
@click.option('-i', '--case-insensitive/--no-case-insensitive', help="Case insensitive completion")
@click.argument('shell', required=False, type=click_completion.DocumentedChoice(click_completion.core.shells))
@click.argument('path', required=False)
def install_autocomplete(append, case_insensitive, shell, path):
    """Install the click-completion-command completion"""
    extra_env = {'_CLICK_COMPLETION_COMMAND_CASE_INSENSITIVE_COMPLETE': 'ON'} if case_insensitive else {}
    shell, path = click_completion.core.install(shell=shell, path=path, append=append, extra_env=extra_env)
    click.echo('%s completion installed in %s' % (shell, path))

cli.add_command(install_autocomplete)
cli.add_command(oci)
cli.add_command(ocs)
cli.add_command(storage)
cli.add_command(account)
