from pyodk.rest import ApiException
from oktawave_cli.common import Api
from pyodk import TicketsApi
from pyodk.rest import ApiException
import time
import logging


class TicketHelper():
    """Docstring for TicketHelper. """

    def __init__(self, api_client):
        """ Setup api_client as TicketHelper member.

        :param api_client: pyodk APICLient

        """
        self._api_client = api_client

    def get_ticket(self, id, max_retry=5):
        """TODO: Docstring for get_ticket.

        :param id: ticket id
        :returns: TODO

        """
        ticket_api = TicketsApi(self._api_client)
        for attempt in range(max_retry):
            try:
                ticket = ticket_api.tickets_get_0(id=id)
                return ticket
            except ApiException as error:
                time.sleep(1)
                if attempt == max_retry - 1:
                    logging.error("Problem with get given ticket %s", error)
                    return None
                continue
