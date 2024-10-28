import requests
import json
import pprint
import os
from dotenv import load_dotenv

URL = "http://localhost:8080/v1/completions"

REQUEST_BODY = '{"language": "", "segments": {"prefix": "", "suffix": ""}}'


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


def get_suggestion(headers, data):
    response = requests.request("POST", url=URL, data=data, headers=headers)
    pprint.pp(response)
    data = response.json()
    return data

def main():
    load_dotenv()
    tabby_auth_token = os.environ["tabby_auth_token"]
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': f'access_token {tabby_auth_token}',
    }
    
    suggestion = get_suggestion(headers, prepare_request_data(
        "python",
        "bucket_sort(my_list: list, bucket_count: int = 10) -> list:",
        ))
    pprint.pp(suggestion["choices"])

if __name__ == "__main__":
    main()


