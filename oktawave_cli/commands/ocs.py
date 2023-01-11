import logging
import click
import sys
from oktawave_cli.common import Api
from oktawave_cli.utils import pretty_print_output, ocs_size_helper
from swiftclient.exceptions import ClientException
from swiftclient.service import SwiftError

logger = logging.getLogger(__name__)

pass_api = click.make_pass_decorator(Api, ensure=True)

@click.group()
@pass_api
def ocs(api):
    """Manage Oktawave Cloud Storage """

@ocs.command("stat")
@click.argument("container", required=False)
@click.argument("object-name", required=False)
@pass_api
def stat(api, container, object_name):
    """ Get statistics about account/container/object.
        If container is not provided it will stat account as default.
        If you want to stat object you need provide container as object exists only in containers.
    """
    def print_rows(headers):
        if container and not object_name:
            if 'X-Container-Read' not in  headers:
                click.echo('X-Container-Read:')
            if 'X-Container-Write' not in  headers:
                click.echo('X-Container-Write:')
        for header, value in headers.items():
            row = f"{header}: {value}"
            click.echo(row)
    if container and not object_name:
        try:
            response = api.swift.stat(container=container)
            headers = response['headers']
            name = f"Container Name: {container}"
            click.echo(name)
            print_rows(headers)
        except ClientException as swift_client_exception:
            click.echo("Problem with stat container", swift_client_exception)
    elif container and object_name:
        try:
            object_list = [object_name]
            for respsone in api.swift.stat(container, object_list):
                headers = response['headers']
                name = f"Object Name: {object_name}"
                click.echo(name)
                print_rows(headers)
        except ClientException as swift_client_exception:
            click.echo("Problem with stat container", swift_client_exception)
    else:
        try:
            response = api.swift.stat()
            headers = response['headers']
            print_rows(headers)
        except ClientException as swift_client_exception:
            click.echo("Problem with stat account", swift_client_exception)


@ocs.command("list")
@click.argument("container", required=False)
@click.option("--human-readable", "-h", is_flag=True, required=False)
@pass_api
def ocs_list(api, container, human_readable):
    """ Lists the containers for the account or the objects for a container.
    :container: container_name
    """
    if not container:
        try:
            resp = api.swift.list()
        except ClientException as swift_client_exception:
            click.echo("Problem with connection to OCS", swift_client_exception)
            sys.exit(-1)
        except SwiftError as err:
            click.echo(err)
            sys.exit(-1)
        if human_readable:
            columns = ["Name", "Object Count", "Size"]
        else:
            columns = ["Name", "Object Count", "Size in Bytes"]
        output = []
        containers  = []
        for part in resp:
            containers = containers + part['listing']
        for container in containers:
            data = []
            size = ocs_size_helper(container['bytes'], human_readable)
            data = [container['name'], container['count'], size]
            output.append(data)
        pretty_print_output(columns, output)
    else:
        try:
            if human_readable:
                columns = ["Object Name", "Object Size", "Last Modified", "Content-Type"]
            else:
                columns = ["Object Name", "Size in Bytes", "Last Modified", "Content-Type"]
            output = []
            objects = []
            try:
                resp = api.swift.list(container)
            except ClientException as swift_client_exception:
                click.echo("Problem with connection to OCS", swift_client_exception)
                sys.exit(-1)
            except SwiftError as err:
                click.echo(err)
                sys.exit(-1)
            for part in resp:
                if part.get("success", False) == True:
                    objects = objects + part['listing']
                else:
                    click.echo(part.get("error"))
            if objects:
                for obj in objects:
                    size = ocs_size_helper(obj['bytes'], human_readable)
                    data = [obj['name'], size,
                            obj['last_modified'], obj['content_type']]
                    output.append(data)
                pretty_print_output(columns, output)
        except ClientException as swift_client_exception:
            message = f"Problem with listing container content, \
            reason: {swift_client_exception.http_reason}"
            click.echo(message)

@ocs.command("post")
@click.argument("container", required=True)
@click.option("--read-acl", "-r", help="Set read ACL on given container")
@click.option("--write-acl", "-w", help="Set write ACL on given container")
@pass_api
def post_container(api, container, read_acl, write_acl):
    """ Create or Modify existing container.

    """
    options = {}
    if read_acl:
        options['read_acl'] = read_acl
    if write_acl:
        options['write_acl'] = write_acl
    try:
        resp = api.swift.stat(container)
    except SwiftError as swift_error:
        if swift_error.exception.http_status == 404:
            resp = api.swift.conn.put_container(container)
    try:
        resp = api.swift.post(container, options=options)
        if resp['success'] is not True:
            click.echo(f"Problem with post on {container}")
    except ClientException as swift_client_exception:
        reason = swift_client_exception.http_reason
        message = f"Problem with creating container, reason: {reason}"
        click.echo(message)

@ocs.command("upload")
@click.argument("container", required=True)
@click.argument("file", required=True)
@pass_api
def upload_file(api, container, file):
    """ Upload file to given container.
    """
    try:
        files = [file]
        resp = api.swift.upload(container, files)
        for part in resp:
            if part['action'] == 'upload_object':
                if part['success'] is  True:
                    click.echo(f"Uploaded: {file}")
    except ClientException as ocs_exception:
        reason = ocs_exception.http_reason
        message = f"Problem with uploading file, reason: {reason}"
        click.echo(message)

@ocs.command("delete")
@click.argument("container", required=True)
@click.argument("object-name", required=False)
@pass_api
def delete_name(api, container, object_name):
    """ Delete given container or object

    """
    try:
        if container and object_name:
            resp = api.swift.delete(container, [object_name])
            for part in resp:
                if part['success'] is not True:
                    click.echo(f"Problem with {part['action']} on {part['name']}")
        else:
            resp = api.swift.delete(container)
            for part in resp:
                if part['success'] is not True:
                    click.echo(f"Problem with {part['action']} on {part['name']}")
    except ClientException as ocs_exception:
        reason = ocs_exception.http_reason
        message = f"Problem with deleting objects, reason: {reason}"
        click.echo(message)
