import os

import requests
import xml.etree.ElementTree as ET
from dotenv import load_dotenv
from pathlib import Path
from requests.auth import HTTPBasicAuth

env_path = Path('../') / '.env'
load_dotenv(dotenv_path=env_path)

url = os.getenv("NEO4J_URI_HTTP_MAGNACLOUDA") + "/db/neo4j/query/v2"
auth = HTTPBasicAuth(os.getenv("NEO4J_USERNAME"), os.getenv("NEO4J_PASSWORD"))

payload = {
    "statement": "MATCH (n:Artist) RETURN n",

}

headers = {
    "Content-Type": "application/json"
}

def artists_test_query():
    response = requests.post(url, json=payload, auth=auth, headers=headers)
    return response.json()





