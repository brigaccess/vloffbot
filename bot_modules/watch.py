import json
import re
import requests
import urllib.parse

from address_cache import cached_address
from database import uses_db
from models import Subscribition, BlackoutAddress, Blackout, Address
from utils import format_blackout

hasnumbers = re.compile('[0-9]')


def geocode_request(q=None, lat=None, lon=None, zoom=15, radius=12):
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


def extract_streetname(item):
    return item['attributes']['street']['abbr'] + ' ' + \
           item['attributes']['street']['name'] + ', ' + \
           item['attributes']['num']


def initialize(tg):
    tg.register_command('/watch', watch_command)


def watch_command(tg, msg):
    chat_id = msg['chat']['id']
    tg.set_handler(chat_id, address_handler)
    tg.send_message(chat_id, _('watch.welcome'))


def address_handler(tg, msg):
    chat_id = msg['chat']['id']
    response = None

    if 'location' in msg:
        response = geocode_request(lat=msg['location']['latitude'], lon=msg['location']['longitude'])
    elif 'text' in msg:
        # Geocoding from address string
        if hasnumbers.search(msg['text']):
            response = geocode_request(q=msg['text'])
    else:
        tg.send_message(chat_id, _('watch.not_expected'))

    if response is None:
        tg.send_message(chat_id, _('watch.blocked_or_broken'))
        return
    elif len(response) > 1:
        multiple_choice(tg, chat_id, response)
    elif len(response) == 1:
        add_watch(tg, chat_id, extract_streetname(response[0]))
    else:
        tg.send_message(chat_id, _('watch.wrong_address'), hide_keyboard=False)


def multiple_choice(tg, chat_id, response):
    kb = []
    for item in response:
        kb.append([extract_streetname(item), ])

    tg.set_handler(chat_id, destiny_handler)
    tg.send_message(chat_id, _('watch.choose_your_destiny'), reply_markup=json.dumps({'keyboard': kb}))


def destiny_handler(tg, msg):
    chat_id = msg['chat']['id']
    tg.set_handler(chat_id, None)
    if 'text' in msg:
        add_watch(tg, chat_id, msg['text'])
    else:
        tg.send_message(chat_id, _('watch.wat'), hide_keyboard=False)


@uses_db
def add_watch(tg, chat_id, address, session=None):
    cached_id = cached_address(address)
    if cached_id is None:
        tg.set_handler(chat_id, None)
        tg.send_message(chat_id, _('watch.blocked_or_broken'))
        return

    if session.query(Subscribition).filter(Subscribition.chat == chat_id,
                                           Subscribition.address_id == cached_id).count() > 0:
        tg.set_handler(chat_id, None)
        tg.send_message(chat_id, _('watch.already_watching'))
        return

    w = Subscribition(chat=chat_id, address_id=cached_address(address))
    session.add(w)
    session.commit()

    current_blackouts = session.query(Address, Blackout) \
        .join(BlackoutAddress, Address.url == BlackoutAddress.address_url) \
        .join(Blackout, BlackoutAddress.blackout_id == Blackout.id) \
        .filter(Address.id == cached_id)

    result_text = ''

    for item in current_blackouts:
        result_text += '\n'
        result_text += format_blackout(_('blackout.format_addressless'), item[0], item[1])

    tg.set_handler(chat_id, None)
    if len(result_text) > 0:
        tg.send_message(chat_id, _('watch.done_with_blackouts') + result_text)
    else:
        tg.send_message(chat_id, _('watch.done'))
