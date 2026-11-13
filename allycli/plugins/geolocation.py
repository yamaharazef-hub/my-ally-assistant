import json
import requests

from plugin import plugin, require


@require(network=True)
@plugin('geolocation')
def geolocation(ally, s):
    """ Helps to geolocate an IP address """
    base_url = "https://api.ip2location.io/"
    payload = {'ip': s, 'format': 'json'}
    ally.say(f'Lookup {s} now...')
    api_result = requests.get(base_url, params=payload)
    api_result_json = api_result.json()
    ally.say(f"It's located at {api_result_json['city_name']}, {api_result_json['region_name']}, {api_result_json['country_name']}.")
    ally.say(f"It's coordinates are ({api_result_json['latitude']}, {api_result_json['longitude']}).")
    ally.say(f"It's owned by {api_result_json['as']} with the ASN {api_result_json['asn']}.")
