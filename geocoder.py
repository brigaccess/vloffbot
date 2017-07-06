import requests
import urllib.parse


def extract_streetname(item):
    return item['attributes']['street']['abbr'] + ' ' + \
           item['attributes']['street']['name'] + ', ' + \
           item['attributes']['num']


def city_filter(response):
    if response is None:
        return None

    filtered = []
    for item in response:
        if item['attributes']['city']['name'] == 'Владивосток':
            filtered.append(item)
    return filtered


def request(q=None, lat=None, lon=None, zoom=15, radius=12):
    url = 'http://api.map.vl.ru/geocode?%s'
    if lat is not None and lon is not None:
        url = url % urllib.parse.urlencode({'lat': lat, 'lon': lon, 'zoom': zoom, 'radius': radius})
    elif q is not None:
        url = url % urllib.parse.urlencode({'q': q})

    try:
        response = requests.get(url).json()
        return response
    except:
        return None
