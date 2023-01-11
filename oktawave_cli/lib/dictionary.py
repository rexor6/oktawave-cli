from pyodk.rest import ApiException
from oktawave_cli.common import Api
from pyodk import DictionariesApi
import logging

IDS = {'system_categories': 70,
       'ip_pools': 76,
       'windows_types': 84,
       'templates_status': 140,
       'authorization_methods': 159,
       'statistics_types': 177,
       'statistics_granulation': 176,
       'oci_status': 27,
       'oci_init_status': 202}

class ApiDictionaryHelper():

    """Class providing logi for Oktawave Dictionary Api endpoint"""

    def __init__(self, api_client):
        """ Setup api_client as ApiDictionaryHelper.

        :param api_client: Oktawave Api client object.

        """
        self._api_instance = DictionariesApi(api_client)

    def get_dictionaries(self):
        """ Get all dictionaries from Oktawave API.
        :returns: dictioners list.

        """
        try:
            dictionaries = self._api_instance.dictionaries_get_dictionaries()
            return dictionaries.items
        except ApiException as api_error:
            logging.error("Could not get dictionares from API. Error: %s", api_error)
            return []

    def get_system_category_dictionaries(self):
        """ Get all dictionaries related to system category.

        :returns: system category dictionary list.

        """
        try:
            ids = IDS['system_categories']
            system_category_dict = self._api_instance.dictionaries_get_dictionaries_items(ids=ids)
            return system_category_dict.items
        except ApiException as api_error:
            logging.error("Could not get dictionares with system categories. Error: %s", api_error)
            return []

    def get_authorization_method_dictionaries(self):
        """ Get all dictionaries related to authorization methods.

        :returns: authorization methods list.

        """
        try:
            ids = IDS['authorization_methods']
            authorization_methods_dict = self._api_instance.dictionaries_get_dictionaries_items(ids=ids)
            return authorization_methods_dict.items
        except ApiException as api_error:
            logging.error("Could not get dictionares with authorization methods. Error: %s", api_error)
            return []

    def get_instance_state_dictionaries(self):
        """ Get all dictionaries related instance status.

        :returns: possible instance status list.

        """
        try:
            ids = IDS['oci_status']
            oci_status_dict = self._api_instance.dictionaries_get_dictionaries_items(ids=ids)
            return oci_status_dict.items
        except ApiException as api_error:
            logging.error("Could not get dictionares with OCI status. Error: %s", api_error)
            return []
