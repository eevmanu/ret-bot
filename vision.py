#!/usr/bin/python
# coding=utf-8

import os
import base64
import urllib2

from googleapiclient import discovery
from googleapiclient import errors
from oauth2client.client import GoogleCredentials

DISCOVERY_URL = 'https://{api}.googleapis.com/$discovery/rest?version={apiVersion}'  # noqa


os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '/home/manuelsolorzano/Projects/hackathon-invoice/final/cloud-vision.json'


class VisionApi:
    """Construct and use the Google Vision API service."""

    def __init__(self, api_discovery_file='vision_api.json'):
        self.credentials = GoogleCredentials.get_application_default()
        self.service = discovery.build(
            'vision', 'v1', credentials=self.credentials,
            discoveryServiceUrl=DISCOVERY_URL)

    def detect_text_from_url(
        self, url, num_retries=3, max_results=6
    ):
        """Uses the Vision API to detect text in the given file.
        """
        response = urllib2.urlopen(url)
        response = response.read()

        batch_request = []
        batch_request.append({
            'image': {
                'content': base64.b64encode(response).decode('UTF-8')
            },
            'features': [{
                'type': 'TEXT_DETECTION',
                'maxResults': max_results,
            }]
        })
        request = self.service.images().annotate(
            body={'requests': batch_request}
        )

        try:
            responses = request.execute(num_retries=num_retries)
            if 'responses' not in responses:
                return {}

            response = responses['responses']
            response = response[0]
            response = response['textAnnotations']
            response = response[0]
            response = response['description']
            response = response.replace('\n', '')
            return response
        except errors.HttpError:
            print("Http Error")
            return None
        except KeyError as e2:
            print("Key error: %s" % e2)
            return None

    def detect_text_from_path(
        self, image_file_path, num_retries=3, max_results=6
    ):
        """Uses the Vision API to detect text in the given file.
        """
        response = ''
        with open(image_file_path, 'rb') as f:
            response = f.read()

        batch_request = []
        batch_request.append({
            'image': {
                'content': base64.b64encode(response).decode('UTF-8')
            },
            'features': [{
                'type': 'TEXT_DETECTION',
                'maxResults': max_results,
            }]
        })
        request = self.service.images().annotate(
            body={'requests': batch_request}
        )

        try:
            responses = request.execute(num_retries=num_retries)
            if 'responses' not in responses:
                return {}

            response = responses['responses']
            response = response[0]
            response = response['textAnnotations']
            response = response[0]
            response = response['description']
            response = response.replace('\n', '')
            return response
        except errors.HttpError:
            print("Http Error")
        except KeyError as e2:
            print("Key error: %s" % e2)
            return None
