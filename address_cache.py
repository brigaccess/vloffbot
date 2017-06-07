import requests
import traceback

from database import uses_db
from models import Address


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
