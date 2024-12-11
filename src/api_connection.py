import requests
import json
import os

from pprint import pprint
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry


class TabbyConnection:
    """
    Connection to tabby server utilities
    """

    def __init__(self, url: str, auth_token: str):
        self._url = url
        self._auth_token = auth_token
        self._session = requests.Session()
        self._session.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"access_token {auth_token}",
        }
        self._adapt_session()

    def _adapt_session(self):
        """
        _summary_
        """
        retry_strategy = Retry(
            total=10,
            backoff_factor=2,
            status_forcelist=[408, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self._session.mount("http://", adapter)
        self._session.mount("https://", adapter)

    def _prepare_request_data(
        self, language: str, prefix: str, suffix: str = None
    ) -> str:
        """
        Prepare body of the post request.
        Parameters
        ----------
        language : str
            programming language of the prefix
        prefix : str
            prefix of the code to get completion for
        suffix : str, optional
            suffix of the code to get completion for, by default None

        Returns
        -------
        str
            formatted body of the post request
        """
        if suffix is None:
            suffix = ""
        request_body = {
            "language": language,
            "segments": {
                "prefix": prefix,
                "suffix": suffix,
            },
        }

        return json.dumps(request_body)

    def _send_post(self, post_data: str) -> dict:
        response = self._session.post(url=self._url, data=post_data, timeout=(60, 120))
        response.raise_for_status()
        response_data = response.json()
        return response_data

    def get_suggestion(self, language: str, prefix: str, suffix: str = None) -> dict:
        post_data = self._prepare_request_data(language, prefix, suffix)
        response_data = self._send_post(post_data)
        return response_data
