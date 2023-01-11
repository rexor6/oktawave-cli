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
from oktawave_cli.lib.storage.ovs import OVS, DISK_TIERS
from oktawave_cli.lib.subregion import SubregionHelper
from oktawave_cli.lib.tickets import TicketHelper
from oktawave_cli.common import Api
from oktawave_cli.utils import pretty_print_output, show_progress_from_ticket

logger = logging.getLogger(__name__)

pass_api = click.make_pass_decorator(Api, ensure=True)


@click.group()
def storage():
    """ Manage Oktwave Volume Storage """

@storage.group()
@pass_api
def ovs(api):
    pass

@ovs.command("list")
@pass_api
def cli_ovs_list(api):
    """ Lists all OVSs """
    ovs = OVS(api.api_client)
    oci_helper = OciHelper(api.api_client)
    disks = ovs.get_all_ovs()
    output = []
    column_names = ["Name", "ID", "Size", "Tier",  "Instance"]
    if disks:
        for disk in disks.items:
            tier_name = DISK_TIERS[str(disk.tier.id)]
            if disk.connections:
                instance_id = disk.connections[0].instance.id
                instance = oci_helper.get_oci_by_id(instance_id)
                instance_name = instance.name
            else:
                instance_name = ""
            instance_data = [disk.name, disk.id, disk.space_capacity, tier_name,
                             instance_name]
            output.append(instance_data)
        pretty_print_output(column_names, output)
    else:
        pretty_print_output(column_names, [[]])


@ovs.command("detach")
@click.option("--ovs-id", type=int, required=True, help="OVS id")
@click.option("--oci-id", type=int, required=True, help="OCI id")
@pass_api
def cli_ovs_detach(api, ovs_id, oci_id):
    """ Disconnects given OVS from given OCI """
    ovs = OVS(api.api_client)
    resp = ovs.detach_ovs_from_instance(ovs_id, oci_id)
    if not resp:
        click.echo("Failed to detach OVS from instance")
        sys.exit(-1)
    ticket_helper = TicketHelper(api.api_client)
    show_progress_from_ticket(resp, ticket_helper)
    ticket = ticket_helper.get_ticket(resp.id)
    if ticket.status.id == 136:
        click.echo("Disk successful detached from instance")
    else:
        click.echo("Problem with detach OVS from instance")

@ovs.command("create")
@click.option("--name", required=True, help="OVS Name")
@click.option("--size", type=int, default=1,
              help="OVS size in GB. Default = 1GB")
@click.option("--tier", type=int, default=48,
              help="OVS Tier. 1 for Tier1, 2 for Tier2, 3 for Tier3, \
             4 for Tier4, 5 for Tier5. Default is Tier1")
@click.option("--subregion-id", type=int, help="Subregion in which create OVS")
@pass_api
def cli_create_ovs(api, name, size, tier, subregion_id):
    """ Creates  new OVS """
    ovs = OVS(api.api_client)
    resp = ovs.create_ovs(name=name, size=size, tier=tier, subregion_id=subregion_id)
    click.echo(resp)


@ovs.command("change-subregion")
@click.option("--ovs-id", required=True, help="OVS id")
@click.option("--subregion-name", help="Subregion Name, e.g. PL1-001")
@click.option("--subregion-id", help="Subregion Id, e.g. 1 for PL1-001,6 for PL-004 etc..")
@click.option("--background", is_flag=True, help="Use for running in background")
@pass_api
def cli_ovs_change_subregion(api, ovs_id, subregion_name, subregion_id,
                            background):
    """ Changes subregion for given OVS """
    if not subregion_name and not subregion_id:
        click.echo("You need to provide subregion-id or subregion-name")
        sys.exit(-1)
    if subregion_name and not subregion_id:
        subregion_api = SubregionHelper(api.api_client)
        subregion = subregion_api.get_subregion_by_name(subregion_name)
        if not subregion:
            click.echo(f"There is no such subregion: {subregion_name}")
            sys.exit(-1)
    ovs = OVS(api.api_client)
    ticket = ovs.change_ovs_subregion(ovs_id, subregion.id)
    ticket_helper = TicketHelper(api.api_client)
    if not background:
        show_progress_from_ticket(ticket, ticket_helper)
        ticket = ticket_helper.get_ticket(ticket.id)
        if ticket.status.id == 136:
            click.echo("Disk successful moved")
        else:
            click.echo("Error while moving disk")
    else:
        click.echo(f"Change subregion operation for OVS started in background. Ticket id: { ticket.id}")
