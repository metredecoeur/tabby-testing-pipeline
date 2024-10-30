import requests
import json
import os

URL = "http://localhost:8080/v1/completions"
FPATH_TABBY_REQUEST_BODY_TEMPLATE = "tabby_request_body.json"


def prepare_request_data(language: str, prefix: str, suffix: str = None) -> str:
    data = {}
    segments = {}
    data["segments"] = segments
    if suffix is None:
        suffix = ""
    data["language"] = language
    data["segments"]["prefix"] = prefix
    data["segments"]["suffix"] = suffix
    return json.dumps(data)


def get_suggestion(data, tabby_auth_token):
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"access_token {tabby_auth_token}",
    }
    response = requests.request("POST", url=URL, data=data, headers=headers)
    response.raise_for_status()
    data = response.json()
    return data
