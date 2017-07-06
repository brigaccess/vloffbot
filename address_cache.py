import re
import requests
import traceback

from database import uses_db
from models import Address
import geocoder

title_re = re.compile('<title>(?:\s*)(.+?)(?:\s*)&mdash;', flags=re.S)


def get_address_url(address):
    try:
        r = requests.post('http://www.vl.ru/off/address/geo/search/json',
                          data={'address': address})
        r = r.json()
        if r['success'] is False:
            return None
        else:
            return r['data'][0]['url']
    except:
        traceback.print_exc()
        return None


@uses_db
def add_address_from_url(address_url, session=None):
    if not address_url.startswith('/off/'):
        address_url = '/off/' + address_url
    if not address_url.endswith('.html'):
        address_url += '.html'

    stored_address = session.query(Address).filter(Address.url == address_url).one_or_none()
    if stored_address is not None:
        return stored_address.id

    try:
        print(address_url)
        r = requests.get('http://www.vl.ru' + address_url)
        if r.status_code == 200:
            addr = title_re.search(r.text)
            if addr:
                addresses = geocoder.city_filter(geocoder.request(q=addr.group(1)))
                if len(addresses) > 1:
                    return None

                address = geocoder.extract_streetname(addresses[0])
                a = Address(address=address, url=address_url)
                session.add(a)
                session.commit()
                session.flush()
                return a.id
    except Exception as e:
        traceback.print_exc()
    return None


@uses_db
def cached_address(address, session=None):
    registered = session.query(Address).filter(Address.address == address).one_or_none()
    if not registered:
        url = get_address_url(address)
        if url is None:
            return None
        a = Address(address=address, url=url)
        session.add(a)
        session.commit()
        session.flush()
        return a.id
    else:
        return registered.id
