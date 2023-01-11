import logging
import configparser
import os
import sys
import pyodk
import oktawave_cli.auth.idserver
import swiftclient.client
from swiftclient.service import SwiftService

logger = logging.getLogger(__name__)

def authwitdh(data, delim):
    """TODO: Docstring for get_max_column_width.

    :param data: rows to callculate len
    :returns: (int) max lenght of column

    """
    colwidth = []
    tempdata = []
    ### ITERATE THROUGH EACH ITEM OF FIRST LIST ###
    for first in range(len(data[0])):
        tempdata.append([])
        ### ITERATE THROUGH EACH LIST  ###
        for item  in range(len(data)):
            ### CREATE A LIST FOR EACH COLUMN ###
            tempdata[item].append(data[first][item])
    ### CREATE A LIST OF MAX COLUMN WIDTHS ###
    for item in range(len(tempdata)):
        cur_max = 0
        for row in tempdata[item][:]:
            if len(row) > cur_max:
                cur_max = len(row)
        colwidth.append(cur_max)
    return colwidth

class Api():

    """Docstring for Config. """

    def __init__(self, project, region='PL1'):
        """TODO: to be defined. """
        username, password, access_id, access_key, ocs_project_name = \
                read_config_project(project)
        self.token = \
                oktawave_cli.auth.idserver.get_access_token(username,
                                                            password,
                                                            access_id,
                                                            access_key)
        if not self.token:
            sys.exit(-1)

        configuration = pyodk.Configuration()
        if region.upper() in('PL2', 'PL-2-KRK'):
            configuration.host = 'https://pl2-api.oktawave.com/services'
            self.region = 'PL2'
        elif region.upper() in ('PL1', 'PL-1-WAW'):
            self.region = 'PL1'
        configuration.access_token = self.token
        self.api_client = pyodk.ApiClient(configuration)
        if ocs_project_name:
            os_options = {'os_project_name': ocs_project_name,
                          'os_project_domain_name': 'OCS',
                          'os_region_name': self.region,
                          'auth_type': 'password',
                          'auth_version': '3',
                          'os_auth_url': 'https://ocs-pl.oktawave.com/auth/v3',
                          'os_password': password,
                          'os_user_id': username}
            self.swift = SwiftService(os_options)


def read_config_project(project):
    """TODO: Docstring for read_config_project.
    :returns: TODO

    """
    config = configparser.ConfigParser()
    config_location = os.path.expanduser('~') + '/.oktawave-cli/config.ini'
    if not os.path.exists(config_location):
        print(f"Error. Could not find config at location: {config_location}")
        sys.exit(-1)
    config.read(config_location)
    username = config[project]['username']
    password = config[project]['password']
    access_id = config[project]['access_id']
    access_key = config[project]['access_key']
    if 'ocs_project_name' in config[project]:
        ocs_project_name = config[project]['ocs_project_name']
    else:
        ocs_project_name = None
    return username, password, access_id, access_key, ocs_project_name
