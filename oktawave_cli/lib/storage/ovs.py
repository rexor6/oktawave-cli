from pyodk.rest import ApiException
from oktawave_cli.common import Api
from pyodk import OVSApi
from pyodk.rest import ApiException
from pyodk import CreateDiskCommand
import time
import logging
import sys

DISK_TIERS= { '48': 'Tier 1',
              '49': 'Tier 2',
              '50': 'Tier 3',
              '895': 'Tier 4',
              '896': 'Tier 5' }

class OVS():

    """Docstring for StorageHelpder. """

    def __init__(self, api_client):
        """ Setup api_client as TicketHelper member.

        :param api_client: pyodk APICLient

        """
        self._api_client = api_client
        self.ovs_api = OVSApi(self._api_client)

    def get_all_ovs(self):
        """TODO: Docstring for get_all_ovs.

        :param f: TODO
        :returns: TODO

        """
        try:
            ovs = self.ovs_api.disks_get_disks(page_size=1000)
        except ApiException as err:
            logging.error("Problem while calling GET /disks/")
            logging.debug("Exception while listinig ovs disks: %s" % err)
            return None
        return ovs


    def get_ovs(self, ovs_id):
        """TODO: Docstring for get_ovs.

        :param ovs_id: TODO
        :returns: TODO

        """
        try:
            ovs = self.ovs_api.disks_get(id=ovs_id)
        except ApiException as e:
            ovs = None
            logging.error("Exception when calling OVSApi->disks_get: %s\n" % e)
        return ovs

    def create_ovs(self, name, size, tier=None, subregion_id=None):
        """TODO: Docstring for create_ovs.

        :param name: TODO
        :param size: TODO
        :param tier: TODO
        :returns: TODO

        """
        command = CreateDiskCommand(disk_name=name, space_capacity=size,
                                    tier_id=tier, subregion_id=subregion_id)
        try:
            resp = self.ovs_api.disks_post(command)
            return resp
        except ApiException as err:
            logging.error("Could not create given OCS: %s" % err)
            return None

    def detach_ovs_from_instance(self, ovs_id, oci_id):
        """TODO: Docstring for detach_ovs_from_instance.

        :param ovs_id: TODO
        :returns: TODO

        """
        ovs = self.get_ovs(ovs_id)
        if not ovs:
            logging.error("Could not find given OVS")
            return None
        try:
            if ovs.connections:
                # In normal conditions it should be always one element list.
                connection = ovs.connections[0]
                if connection.instance.id != oci_id:
                    logging.error("Given OVS: %s is not connected to given OCI")
                    return None
                elif connection.is_system_disk:
                    logging.error("You can't detach system disk from OCI")
                    return None
            else:
                logging.error("Given OVS is not connected to any instance")
                sys.exit(-1)
            resp = self.ovs_api.disks_detach_from_instance(ovs_id, oci_id)
            return resp
        except ApiException as e:
            logging.error("Exception when calling OVSApi->disks_detach_from_instance: %s\n" % e)
            sys.exit(-1)

    def change_ovs_tier(self, ovs_id, tier_id, asynchronous=False):
        """TODO: Docstring for change_ovs_tier.

        :param ovs_id: TODO
        :param tier_id: TODO
        :returns: Ticket
                  If the method is called asynchronously,
                  returns the request thread.

        """
        try:
            ticket = self.ovs_api.disks_change_tier(id=ovs_id, tier_id=tier_id,
                                                async_req=True)
        except ApiException as err:
            logging.error("Exception when calling OVSApi->disks_change_tier")
            logging.debug("Exception: %s" % err)
            return None
        return ticket

    def change_ovs_subregion(self, ovs_id, subregion_id):
        """TODO: Docstring for change_ovs_subregion.

        :param int ovs_id: OVS id
        :param int subregion_id: Subregion Id
        :returns: Ticket

        """
        try:
            ticket = self.ovs_api.disks_change_subregion(id=ovs_id,
                                                    subregion_id=subregion_id)
        except ApiException as err:
            logging.error("Exception when calling OVSApi->disk_change_tier")
            logging.debug("Exception: %s" % err)
            return None
        return ticket

