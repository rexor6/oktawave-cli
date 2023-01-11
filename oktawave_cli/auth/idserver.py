import requests
import json
import logging

logger = logging.getLogger(__name__)

def get_access_token(login, password, access_id, access_key,
                     idserver='https://id.oktawave.com'):
    """ Gets Oktawave bearer token

    :param login: login
    :param password: password for given loging
    :param access_id: API access id
    :param access_key: API access key
    :param idserver: idServer URL
    :returns: bearer token if succesful otherwise None

    """
    logger.debug("test")
    token_url = idserver + '/core/connect/token'
    data = {
        'grant_type': 'password',
        'username': login,
        'password': password,
        'scope': 'oktawave.api offline_access'
    }
    auth = (access_id, access_key)
    try:
        resp = requests.post(token_url, data=data, auth=auth, verify=True)
    except requests.ConnectTimeout:
        logging.error("Connection timeout while connecting to idServer")
        return None
    except requests.RequestException:
        logging.error("There was some problem while connecting to idServer")
        return None
    if resp.status_code == 400:
        logging.error("Couldn't retrieve access token.Check your config")
    if resp.status_code != 200:
        return None
    data = resp.json()
    try:
        token = data['access_token']
    except Exception as err:
        return None
    return token
