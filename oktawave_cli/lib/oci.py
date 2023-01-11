from pyodk.rest import ApiException
from oktawave_cli.common import Api
from pyodk import OCIApi, OCITemplatesApi, CreateInstanceCommand, TicketsApi, OVSApi
import logging
import json


logger = logging.getLogger(__name__)
logger.setLevel(level=logging.DEBUG)

class OciHelper(object):

    """Docstring for OciHelper. """

    def __init__(self, api_client):
        """ Setup api_client as OciHelper member.

        :param api_client: pyodk APICLient

        """
        self._api_client = api_client


    def get_oci_list(self):
        """ Connect with given ApiClient to Oktawave and gets OCI collection list.

        :param api_client: pyodk APIClient
        :returns: pyodk.ApiCollectionInstance: list of instances

        """
        try:
            oci_api = OCIApi(self._api_client)
            instances = oci_api.instances_get(page_size=65535)
            return instances.items
        except ApiException as api_error:
            logger.error("Error while getting OCI list %s", api_error)
            return []

    def get_oci(self, oci_name=None, oci_id=None):
        """ Connect with given ApiClient to Oktawave and gets OCI collection list.

        :param api_client: pyodk APIClient
        :returns: pyodk.ApiCollectionInstance: list of instances

        """
        if oci_name is  None and oci_id is None:
            logging.error("Bad input, you need to provide OCI Name or ID")
            return None
        try:
            instances = self.get_oci_list()
            if len(instances) == 0:
                return []
            oci_list = []
            for instance in instances:
                if oci_name:
                    if instance.name == oci_name:
                        oci_list.append(instance)
                elif oci_id:
                    if instance.id == oci_id:
                        oci_list.append(instance)
            return oci_list
        except ApiException as api_error:
            logging.error("Error while getting OCI list %s", api_error)
            return None

    def get_oci_by_id(self, oci_id=None):
        """ Connect with given ApiClient to Oktawave and gets OCI"

        :param api_client: pyodk APIClient
        :returns: pyodk.ApiCollectionInstance: list of instances

        """
        oci_api = OCIApi(self._api_client)
        try:
            instance = oci_api.instances_get_0(oci_id)
            return instance
        except ApiException as api_error:
            logging.error("Error while getting given OCI list %s", api_error)
            return None

    def create_oci(self, name, **params):
        """ Create OCI with given params.

        :param **params: key,value list of parameters
        :returns:

        """
        oci_api = OCIApi(self._api_client)
        command = CreateInstanceCommand(instance_name=name, **params)
        try:
            resp = oci_api.instances_post(command)
            return resp
        except ApiException as api_error:
            logging.error("Problem with creating OCI %s", api_error)
            return None

    def delete_oci(self, name=None, oci_id=None, deep=False):
        """ Delete given OCI.

        :param name: TODO
        :param id: TODO
        :returns: True if all vms deleted, otherwise False.

        """
        #TODO do przebudowy, rozbic na dwie funkcje, zwracac ticket
        oci_api = OCIApi(self._api_client)
        if name:
            instances = self.get_oci(oci_name = name)
        elif oci_id:
            instances = self.get_oci(oci_id=oci_id)
        else:
            logging.error("You need to provide name or id")
            return False
        if len(instances) == 0:
            logging.info("Could not find given OCI")
            return False
        for instance in instances:
            result  = True
            try:
                oci_api.instances_delete(instance.id, deep=deep)
            except ApiException as delete_error:
                error_body = json.loads(delete_error.body)
                error_message = f"Problem with deleting OCI. Message from API: {error_body['Message']}, error id: {error_body['ErrorId']}"
                logging.error(error_message)
                logging.debug("Exception when calling pyodk->OCIApi->instances_change_type: %s\n",
                              delete_error)
                result = False
        return result

    def diconnect_ovs_from_instance(self, ovs_id):
        """TODO: Docstring for diconnect_ovs.

        :param ovs_id: TODO
        :returns: TODO

        """
        ovs_api = OVSApi(self._api_client)
        try:
            ovs_api.disks_get_disks
        except Exception as e:
            print(e)

    def get_instances_types(self, order_by=None):
        """ Get all instances_types.

        :param arg1: TODO
        :returns: TODO

        """
        oci_api = OCIApi(self._api_client)
        if order_by:
            types = oci_api.instances_get_instances_types(order_by=order_by)
        else:
            types = oci_api.instances_get_instances_types()
        return types.items


    def get_instances_type(self, type_name=None, type_id=None):
        """ Lookup for given type of instance and return it.

        :param type_name: name of type.
        :param  type_id: id of type.
        :returns: given type or None if could not find it.

        """
        types = self.get_instances_types()
        for oci_type in types:
            if type_name:
                if oci_type.name == type_name:
                    return oci_type
            elif type_id:
                if oci_type.id == type_id:
                    return oci_type
        return None

    def change_oci_class(self, oci_name=None, oci_id=None, oci_type_name=None, oci_type_id=None):
        """TODO: Set OCI with given class.

        :param oci_class: TODO
        :param oci_name: TODO
        :param oci_id: TODO
        :returns: TODO

        """
        tickets = []
        oci_api = OCIApi(self._api_client)
        if oci_name:
            instances = self.get_oci(oci_name=oci_name)
        elif oci_id:
            instances = self.get_oci(oci_name=oci_name)
        if len(instances) < 1:
            logging.info("Could not find given OCI")
            return False

        if oci_type_id:
            oci_type = self.get_instances_type(type_id=oci_type_id)
        elif oci_type_name:
            oci_type = self.get_instances_type(type_id=oci_type_id)

        for instance in instances:
            ticket  = oci_api.instances_change_type_0(instance.id, type_id=oci_type.id)
            tickets.append(ticket)
        return tickets

    def get_templates(self, order_by='SystemCategory'):
        """TODO: Docstring for get_templates.
        :returns: TODO

        """
        templates_api = OCITemplatesApi(self._api_client)
        try:
            all_templates = templates_api.templates_get(page_size=65535, order_by=order_by)
            return all_templates.items
        except ApiException as api_error:
            logging.error("Could not get template lists. Error: %s", api_error)
            return []

    def reboot_oci(self, oci_id):
        """TODO: Docstring for reboot_oci.
        :param oci_id: TODO
        :returns: TODO

        """
        if not oci_id:
            return False

        oci_api = OCIApi(self._api_client)
        resp = oci_api.instances_reboot(id=oci_id)
        return resp

    def restart_oci(self, oci_id):
        """TODO: Docstring for reboot_oci.
        :param oci_id: TODO
        :returns: TODO

        """
        if not oci_id:
            return False

        oci_api = OCIApi(self._api_client)
        resp = oci_api.instances_reset(id=oci_id)
        return resp

    def poweron_oci(self, oci_id):
        """TODO: Docstring for reboot_oci.
        :param oci_id: TODO
        :returns: TODO

        """
        if not oci_id:
            return False

        oci_api = OCIApi(self._api_client)
        resp = oci_api.instances_power_on(id=oci_id)
        return resp

    def poweroff_oci(self, oci_id):
        """TODO: Docstring for reboot_oci.
        :param oci_id: TODO
        :returns: TODO

        """
        if not oci_id:
            return False

        oci_api = OCIApi(self._api_client)
        resp = oci_api.instances_power_off(id=oci_id)
        return resp

    def get_dns_name(self, oci_id):
        """ Get DNS name for given OCI

        :param oci_id: ID of OCI
        :returns: (string) OCI dns name

        """
        oci_api = OCIApi(self._api_client)
        instance = oci_api.instances_get_0(id=oci_id)
        if instance:
            return instance.dns_address
        return None
