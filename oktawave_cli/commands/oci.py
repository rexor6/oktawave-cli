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
from oktawave_cli.lib.subregion import SubregionHelper
from oktawave_cli.lib.tickets import TicketHelper
from oktawave_cli.common import Api
from oktawave_cli.utils import pretty_print_output, show_progress_from_ticket

logger = logging.getLogger(__name__)

pass_api = click.make_pass_decorator(Api, ensure=True)

@click.group()
@pass_api
def oci(api):
    """Manage Oktawave Cloud Instances"""

@oci.command("list")
@pass_api
def oci_list(api):
    """Gets OCI list."""
    oci_helper = OciHelper(api.api_client)
    instances = oci_helper.get_oci_list()
    output = []
    column_names = ["Name", "ID", "Status",  "IP", "Class"]
    for instance in instances:
        instance_data = [instance.name, instance.id, instance.status.label,
                         instance.ip_address, instance.type.label]
        output.append(instance_data)
    pretty_print_output(column_names, output)

@oci.command("get")
@click.option("--name", help="Name of instance")
@click.option("--oci-id", type=int, help="Id of instance")
@pass_api
def oci_get(api, name, oci_id):
    """Get  OCI."""
    column_names = ["Name", "ID", "IP", "Class"]
    output = []
    if not name and not oci_id:
        click.echo("You must provide name or id of oci")
        return -1

    oci_helper = OciHelper(api.api_client)
    if oci_id:
        instance = oci_helper.get_oci_by_id(oci_id)
        instance_data = [[instance.name, instance.id, instance.ip_address,
                          instance.type.label]]
        pretty_print_output(column_names, instance_data)
        return 0

    instances = oci_helper.get_oci(oci_name=name)
    output = []
    if instances:
        for instance in instances:
            instance_data = [instance.name, instance.id]
            output.append(instance_data)
        pretty_print_output(column_names, output)
    else:
        click.echo(f"Could not find instance with name: {name}")

@oci.command("types")
@pass_api
@click.option("--order-by", default="CPU",
              help="Available orders are: Category, Cpu, Ram, Name. Default=CPU")
def get_oci_types(api, order_by):
    """Print available OCI types(class)."""

    column_names = ["Name", "ID", "CPU", "RAM", "Category"]
    oci_helper = OciHelper(api.api_client)
    if order_by.lower() not in ('cpu', 'ram', 'name', 'category', 'none'):
        click.echo("You can order only by: CPU, RAM, Name, Category or None")
    if order_by.lower() == 'none':
        returned_types = oci_helper.get_instances_types(order_by=None)
    else:
        returned_types = oci_helper.get_instances_types(order_by=order_by)
    output = []
    for oci_type in returned_types:
        type_data = [oci_type.name, oci_type.id,
                     oci_type.cpu, oci_type.ram,
                     oci_type.category.label]
        output.append(type_data)
    pretty_print_output(column_names, output)

@oci.command("templates")
@pass_api
def templates_list(api):
    """List of available templates."""

    columns = ['Name', 'ID', 'System Category', "Owner Account"]
    oci_helper = OciHelper(api.api_client)
    templates = oci_helper.get_templates()
    output = []
    for template in templates:
        template_data = [template.name, template.id,
                         template.system_category.label,
                        template.owner_account]
        output.append(template_data)
    pretty_print_output(columns, output)


@oci.command("create")
@pass_api
@click.option("--name", help="Name for created OCI", required=True)
@click.option("--template-id", type=int, help="Template id", required=True)
@click.option("--authorization-method", default="ssh", help="Authorization method. SSH or Password")
@click.option("--disk-class", help="Type 48 for Tier1, 49 for Tier2, 50 for Tier3, 895 for Tier4, 896 for Tier5")
@click.option("--disk-size", type=int, help="Initial disk size")
@click.option("--ip-address-id", help="Public IP id. Create OCI with given ip")
@click.option("--ssh-key", help="IDs of ssh keys", multiple=True)
@click.option("--subregion", help="Subregion name in which create OCI for example: PL-001")
@click.option("--type-id", default=1047, type=int, help="Instance Type")
@click.option("--init-script", help="Location of puppet manifiest to send to OCI")
@click.option("--without-publicip", is_flag=True, help="Create OCI whitout public IP")
@click.option("--count", type=int, help="Count of instances to create")
def oci_create(api, name, template_id, authorization_method,
              disk_class, disk_size, ip_address_id, ssh_key, subregion, type_id,
              init_script, without_publicip, count):
    """Create OCI."""

    args_dict = {}
    if authorization_method.lower() == 'ssh' and not ssh_key:
        click.echo("You need provide ssh-keys to add")
        sys.exit(-1)
    if without_publicip and ip_address_id != 0:
        click.echo("Bad options, don't use --without-publicip flag with --ip-address")
        sys.exit(-1)
    if authorization_method.lower() == 'ssh':
        authorization_method_id = 1398
        key_ids = list(ssh_key)
        args_dict['ssh_keys_ids'] = key_ids
    elif authorization_method.lower() == 'password':
        authorization_method_id = 1399
    args_dict['authorization_method_id'] = authorization_method_id

    # find subregion
    if subregion:
        subregion_name = subregion.lower()
        subregion_helper = SubregionHelper(api.api_client)
        api_subregions = subregion_helper.get_subregions()
        found = False
        for api_subregion in api_subregions.items:
            if api_subregion.name.lower() == subregion_name:
                found = True
                if not api_subregion.is_active:
                    click.echo("Given subregion is not active")
                    sys.exit(-1)
                args_dict['subregion_id'] = api_subregion.id
        if not found:
            click.echo(f"There is no such subregion: {subregion}")
            sys.exit(-1)

    # set disk size
    if disk_size:
        args_dict['disk_size'] = disk_size
    if type_id:
        args_dict['type_id'] = type_id
    if count:
        args_dict['instances_count'] = count
    args_dict['template_id'] = template_id
    oci_helper = OciHelper(api.api_client)
    resp = oci_helper.create_oci(name, **args_dict)
    if not resp:
        click.echo("Problem with creating OCI")
        sys.exit(-1)
    ticket_helper = TicketHelper(api.api_client)
    click.echo("Creating OCI in progress...")
    show_progress_from_ticket(resp, ticket_helper)
    ticket = ticket_helper.get_ticket(resp.id)
    if ticket.status.id == 137:
        click.echo("Error while creating OCI")
    else:
        click.echo("Successful created OCI")

@oci.command("reboot")
@pass_api
@click.option("--id", 'oci_id', type=int, help="Id of OCI")
@click.option("--force", help="Reboot without confirm")
def oci_reboot(api, oci_id, force):
    """Will try to soft(warm) reboot OCI."""
    if not id:
        click.echo("You need to provide OCI id.")
    oci_helper = OciHelper(api.api_client)
    instance = oci_helper.get_oci_by_id(oci_id=oci_id)

    if not force:
        if not click.confirm(f"Are you really want to reboot OCI {instance.name}?"):
            click.echo("Aborting")
            sys.exit(-1)
    resp = oci_helper.reboot_oci(oci_id=oci_id)
    if resp:
        ticket_helper = TicketHelper(api.api_client)
        ticket_id = resp.id
        ticket = ticket_helper.get_ticket(ticket_id)
        with click.progressbar(length=100) as progress_bar:
            click.echo("Rebooting OCI in progress...")
            while ticket.status.id == 135 and ticket.progress != 100:
                ticket = ticket_helper.get_ticket(ticket_id)
                progress_bar.update(ticket.progress)
        if ticket.status.id == 136:
            click.echo("Successful rebooted OCI")
        else:
            click.echo("Error while soft rebooting OCI.")

@oci.command("restart")
@pass_api
@click.option("--id", 'oci_id', type=int, help="Id of OCI")
@click.option("--name", 'oci_name', type=int, help="Id of OCI")
@click.option("--force", help="Restart without confirm")
def oci_restart(api, oci_id, oci_name, force):
    """Hard restart OCI."""
    if not id:
        click.echo("You need to provide OCI id.")
    oci_helper = OciHelper(api.api_client)
    instance = oci_helper.get_oci_by_id(oci_id=oci_id)

    if not force:
        click.confirm(f"Are you really want to restart OCI {instance.name}?")
    resp = oci_helper.restart_oci(oci_id=oci_id)
    if resp:
        ticket_helper = TicketHelper(api.api_client)
        ticket_id = resp.id
        ticket = ticket_helper.get_ticket(ticket_id)
        with click.progressbar(length=100) as progress_bar:
            click.echo("Restarting OCI in progress...")
            while ticket.status.id == 135 and ticket.progress != 100:
                ticket = ticket_helper.get_ticket(ticket_id)
                progress_bar.update(ticket.progress)
        if ticket.status.id == 136:
            click.echo("Successful restarted OCI")
        else:
            click.echo("Error while soft restarting OCI.")

@oci.command("poweron")
@pass_api
@click.option("--id", 'oci_id', type=int, help="Id of OCI")
@click.option("--name", 'oci_name', help="Name of OCI")
def oci_poweron(api, oci_id, oci_name):
    """ PowerOn OCI."""
    if not id:
        click.echo("You need to provide OCI id.")
    oci_helper = OciHelper(api.api_client)
    resp = oci_helper.poweron_oci(oci_id=oci_id)

    if resp:
        ticket_helper = TicketHelper(api.api_client)
        ticket_id = resp.id
        ticket = ticket_helper.get_ticket(ticket_id)
        with progressbar.ProgressBar(max_value=100) as progress_bar:
            click.echo("Power on  OCI in progress...")
            while ticket.status.id == 135 and ticket.progress != 100:
                ticket = ticket_helper.get_ticket(ticket_id)
                progress_bar.update(ticket.progress)
        if ticket.status.id == 136:
            click.echo("Successful powered on OCI")
        else:
            click.echo("Error while powering on OCI.")

@oci.command("poweroff")
@pass_api
@click.option("--id", 'oci_id', type=int, required=True, help="Id of OCI")
@click.option("--force", is_flag=True, help="Force poweroff OCI")
def oci_poweroff(api, oci_id, force):
    """ PowerOff OCI."""
    oci_helper = OciHelper(api.api_client)
    instance = oci_helper.get_oci_by_id(oci_id=oci_id)

    if not force:
        if not click.confirm(f"Are you really want to poweroff OCI {instance.name}?"):
            click.echo("Aborting")
            sys.exit(-1)
    resp = oci_helper.poweron_oci(oci_id=oci_id)
    if resp:
        ticket_helper = TicketHelper(api.api_client)
        ticket_id = resp.id
        ticket = ticket_helper.get_ticket(ticket_id)
        with click.progressbar(length=100) as progress_bar:
            click.echo("Poweroff OCI in progress...")
            while ticket.status.id == 135 and ticket.progress != 100:
                ticket = ticket_helper.get_ticket(ticket_id)
                progress_bar.update(ticket.progress)
        if ticket.status.id == 136:
            click.echo("Successful powered off OCI")
        else:
            click.echo("Error while powering off OCI.")

@oci.command("delete")
@pass_api
@click.option("--id", "oci_id", type=int, required=True, help="Id of OCI")
@click.option("--force", is_flag=True, help="Delete without confirm")
@click.option("--deep", is_flag=True, help="Delete OCI with all attached OVS")
def oci_delete(api, oci_id, force, deep):
    """Delete OCI."""
    if not force:
        if not click.confirm("Are you sure?"):
            click.echo("Aborting")
            sys.exit(-1)
    oci_helper = OciHelper(api.api_client)
    status = oci_helper.delete_oci(oci_id=oci_id, deep=deep)
    if not status:
        click.echo("Problem with deleting OCI.")
        sys.exit(-1)
    if status:
        click.echo("Successful deleted OCI")
    else:
        click.echo("Error while deleting OCI")

@oci.command("ssh")
@pass_api
@click.option("--id", "oci_id", type=int, required=True, help="Id of OCI")
@click.option("--login", help="Use  login for connection")
def oci_ssh(api, oci_id, login):
    """Connect to OCI by ssh."""
    oci_helper = OciHelper(api.api_client)
    dns_name = oci_helper.get_dns_name(oci_id)
    if not dns_name:
        click.echo("Could not get DNS Name for OCI")
        sys.exit(-1)
    where = f"root@{dns_name}"
    subprocess.call(['ssh', where])
