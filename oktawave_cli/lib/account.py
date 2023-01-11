from pyodk.rest import ApiException
from oktawave_cli.common import Api
from pyodk import AccountApi
import logging

class AccountHelper(object):

    """Account API helper class """

    def __init__(self, api_client):
        self.api_instance = AccountApi(api_client)

    def get_ssh_keys(self):
        """ Get ssh keys list
        :returns: ApiColectionSshKeys

        """
        try:
            ssh_keys_collection = self.api_instance.account_get_ssh_keys()
        except ApiException as err:
            logging.error("Problem with getting ssh keys %s", err)
            return None
        return ssh_keys_collection

    def get_ssh_key(self, ssh_key_id):
        """ Gets given ssh key

        :param ssh_key_id: ssh key idj
        :returns: Return given ssh key if found othwerwise None

        """
        try:
            ssh_key = self.api_instance.account_get_ssh_key(ssh_key_id)
        except ApiException as err:
            logging.error("Problem with geting ssh key id: %d, error: %s", id,err)
            return None
        return ssh_key

    def delete_ssh_key(self, ssh_key_id):
        """ Deletes given ssh key

        :param ssh_key_id: ssh key id
        :returns: True if successful otherwise False

        """
        try:
            response = self.api_instance.account_delete_ssh_key(ssh_key_id)
        except ApiException as err:
            logging.error("Error while deleting given ssh key %s", err.body)
            return False
        return True

    def get_account_detail(self):
        """ Gets  account details

        :returns: account detail

        """
        try:
            account_detail = self.api_instance.account_get()
        except ApiException as err:
            logging.error("Problem with getting account detail %s", err)
            return None
        return account_detail
