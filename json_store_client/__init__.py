import json

import jsonpickle
import requests

DEFAULT_TIMEOUT_SECONDS = 5


class JsonstoreError(Exception):
    """Exception for errors occurring in calls to Jsonstore"""
    pass


class Client:
    """Http client for the www.jsonstore.io API

    Attributes:
        __base_url Base url for jsonstore, including a user token.
        __headers  Request headers to include in all requests to jsonstore.
    """

    def __init__(self, token: str):
        self.session = requests.Session()
        self.session.headers.update({
            'Accept': 'application/json',
            'Content-type': 'application/json'
            })
        self.__base_url = f'https://www.jsonstore.io/{token}'

    def get(self, key: str, timeout: int = DEFAULT_TIMEOUT_SECONDS):
        """Get gets value from jsonstore.

        :param key: Name of key to a resource
        :param timeout: Timeout of the request in seconds
        :return: Response result as a dictionary
        """
        url = self.__finalize_url(key)
        try:
            resp = self.session.get(url, timeout=timeout)
            print(resp.headers)
            json_resp = self.__check_response(resp)
            return jsonpickle.decode(json_resp['result'])
        except (ValueError, KeyError) as e:
            raise JsonstoreError(str(e))

    def save(self, key: str, data, timeout: int = DEFAULT_TIMEOUT_SECONDS):
        """Save data in jsonstore under a key.

        :param key:str Name of key to a resource
        :param data:any Data to be updated, will be dumped with jsonpickle.
        :param timeout:int Timeout of the request in seconds
        """
        url = self.__finalize_url(key)
        json_data = json.dumps(jsonpickle.encode(data))
        try:
            resp = self.session.post(url, data=json_data, timeout=timeout)
            self.__check_response(resp)
        except (ValueError, KeyError) as e:
            raise JsonstoreError(str(e))

    def delete(self, key: str, timeout: int = DEFAULT_TIMEOUT_SECONDS):
        """Deletes data in jsonstore under a key.

        :param key:str Name of key to a resource
        :param timeout:int Timeout of the request in seconds
        """
        url = self.__finalize_url(key)
        try:
            resp = self.session.delete(url,
                                       timeout=timeout)
            self.__check_response(resp)
        except (ValueError, KeyError) as e:
            raise JsonstoreError(str(e))

    def __check_response(self, response):
        """Checks if a response is successful raises a JsonstoreError if not.

        :param response: Response to check
        :return: Deserialized json response
        """
        if not isinstance(response, requests.Response):
            raise TypeError('Unexpected type {}'.format(type(response)))
        response.raise_for_status()
        resp = response.json()
        if 'ok' not in resp:
            raise JsonstoreError('Call to jsonstore failed')
        return resp

    def __finalize_url(self, key):
        """Creates url for a given key.

        :param key: Key to append to the base url
        :return: URL to resource
        """
        return '{}/{}'.format(self.__base_url, key)