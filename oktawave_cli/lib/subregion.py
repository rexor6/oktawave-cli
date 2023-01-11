from pyodk.rest import ApiException
from oktawave_cli.common import Api
from pyodk import SubregionsApi
import logging

class SubregionHelper(object):

    """Docstring for OciHelper. """

    def __init__(self, api_client):
        """ Setup api_client as OciHelper member.

        :param api_client: pyodk APICLient

        """
        self._api_client = api_client

    def get_subregions(self):
        """ Get subregions in region.

        :returns: list of subregions

        """
        try:
            subregion_api = SubregionsApi(self._api_client)
            subregions = subregion_api.subregions_get()
        except Exception as err:
            logging.error("Error while getting subregion list")
            logging.debug("Exception: %s" % err)
            return None
        return subregions

    def get_subregion_by_name(self, subregion_name):
        """TODO: Docstring for get_subregion_by_name.

        :param arg1: TODO
        :returns:  Subregion

        """
        subregions = self.get_subregions()
        subregion_name = subregion_name.lower()
        if subregions:
            for subregion in subregions.items:
                if subregion.name.lower() == subregion_name:
                    return subregion
        return None
