import requests

def list_aircraft(url):
    return requests.get(url).json()["aircraft"]

