import requests
import logging
from requests import Response
from requests.exceptions import HTTPError, ConnectionError
from http import HTTPStatus
import time
from typing import List
import json
from datetime import datetime

from endpoints import download_endpoint
from mylogging import log_setup

#set up logging configuration
log_setup()
logger = logging.getLogger(__name__)

retry_in: int = 10  # seconds
retries: int = 3
retry_codes: List = [
    HTTPStatus.BAD_GATEWAY,
    HTTPStatus.SERVICE_UNAVAILABLE,
    HTTPStatus.GATEWAY_TIMEOUT,
    HTTPStatus.TOO_MANY_REQUESTS,
    HTTPStatus.INTERNAL_SERVER_ERROR,
]

DATA_ID_JSON_FILENAME = 'data_id.json'
endpoints_names = ('Written exam', 'Trial exam', 'General news')


class Fetcher:

    def __init__(self):
        self.headers = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-IN,en-US;q=0.9,en;q=0.8,ms-MY;q=0.7,ms;q=0.6,en-GB;q=0.5',
            'Connection': 'keep-alive',
            'Origin': 'http://tmolicense.lumbini.gov.np',
            'Referer': 'http://tmolicense.lumbini.gov.np/',
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36',
        }
        self.params = {
            'pageNo': '0',
            'pageSize': '10',
        }

    def get_endpoint_name(self, endpoint):
        endpoint_name = endpoint.split("/")[-1]
        if endpoint_name == 'written-forms':
            endpoint_name = endpoints_names[0]
        elif endpoint_name == 'forms':
            endpoint_name = endpoints_names[1]
        elif endpoint_name == 'news-events':
            endpoint_name = endpoints_names[2]
        return endpoint_name

    def fetch_forms(self, endpoint: str):
        """Fetches the response for the given endpoint"""
        for n in range(retries):
            try:
                logger.info(
                    f'Fetching {self.get_endpoint_name(endpoint=endpoint)} ..attempt {n+1}')
                response = requests.get(
                    endpoint,
                    params=self.params,
                    headers=self.headers,
                    verify=False,
                )

                response.raise_for_status()
                return response
            except HTTPError as exception:
                logger.error(exception)
                code = exception.response.status_code
                if code in retry_codes:
                    logger.info('retrying in {retry_in} seconds...')
                    time.sleep(retry_in)
                    continue
            except ConnectionError as connection_error:
                logger.error(connection_error)
                logger.info('retrying in {retry_in} seconds...')
                time.sleep(retry_in)
                continue
            except Exception as gemeral_exception:
                logger.error(gemeral_exception)
                return None
        return None

    def get_title_downloadfileUrl_formatteddate(self, dataobject: dict, endpoint_name):
        title = dataobject['title']
        fileUrl = dataobject['fileUrl']
        createdDate = dataobject['createdDate']
        download_fileUrl = "/".join((download_endpoint, fileUrl))
        formatted_date = datetime.strptime(
            createdDate, '%Y-%m-%dT%H:%M:%S.%f').strftime('%b/%d %I:%M %p')
        return title, download_fileUrl, formatted_date, endpoint_name

    def first_feed(self, responseObject_data: list, endpoint_name: str):
        contents = []
        for data in responseObject_data[:5]:
            contents.append(self.get_title_downloadfileUrl_formatteddate(data, endpoint_name))
        return contents

    def update_id(self, endpoint_name: str):
        raise NotImplementedError

    def response_hanlder(self, response: Response, endpoint: str):

        endpoint_name = self.get_endpoint_name(endpoint=endpoint)
        # Base check to see if the response is None
        if not response:
            logger.info(
                f'Unable to get response from {endpoint_name} endpoint!')
            return None

        try:
            responseObject_data: list = response.json()['responseObject']['data']
            latest_data_object: dict = responseObject_data[0]
            latest_id: int = latest_data_object.get('id', None)
        except TypeError as te:
            logger.error(te)
            return None
        except KeyError as ke:
            logger.error(ke)
            return None

        try:
            with open(DATA_ID_JSON_FILENAME, 'r') as json_file:
                data_ids: dict = json.load(json_file)

        except (FileNotFoundError, json.decoder.JSONDecodeError):
            logger.info(f'File {DATA_ID_JSON_FILENAME} not found!')
            temp_data = {
                endpoint_name: latest_id
            }
            with open(DATA_ID_JSON_FILENAME, 'w') as json_file:
                json.dump(temp_data, json_file)
            logger.info(f'{DATA_ID_JSON_FILENAME} created and with id={latest_id}')
            data_ids = {}

        cached_id = data_ids.get(endpoint_name, None)
        if not cached_id:
            data_ids.update({endpoint_name: latest_id})
            with open(DATA_ID_JSON_FILENAME, 'w') as json_file:
                json.dump(data_ids, json_file)
            logger.info(f'{endpoint_name} tracking with id={latest_id}')
            return self.first_feed(responseObject_data, endpoint_name)

        elif not latest_id == cached_id:
            logger.info(
                f'New entry found for {endpoint_name} notice! id: {latest_id}')
            
            # Updating the endpoint cached id
            data_ids.update({endpoint_name: latest_id})
            with open(DATA_ID_JSON_FILENAME, 'w') as json_file:
                json.dump(data_ids, json_file)
            logger.info(f'{endpoint_name} updated id={latest_id}')

            contents = []
            for data in responseObject_data:
                contents.append(self.get_title_downloadfileUrl_formatteddate(data, endpoint_name))
                if data['id'] == latest_id:
                    break
            return contents
            # title, download_fileUrl, formatted_date, endpoint_name = self.get_title_downloadfileUrl_formatteddate(
            #     dataobject=latest_data_object, endpoint_name=endpoint_name)

            # return [(title, download_fileUrl, formatted_date, endpoint_name)]
        logger.info(f'No new update found for {endpoint_name} notices')
        return None
