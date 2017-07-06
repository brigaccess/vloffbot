import json
import re

from address_cache import cached_address
from utils import subscribe, SubscribeStatus
import geocoder

hasnumbers = re.compile('[0-9]')


def initialize(tg):
    tg.register_command('/watch', watch_command)


def watch_command(tg, msg):
    chat_id = msg['chat']['id']
    msg_id = msg['message_id']
    tg.set_handler(chat_id, address_handler)
    tg.reply(chat_id, msg_id, _('watch.welcome'), dialogue=True)


def address_handler(tg, msg):
    chat_id = msg['chat']['id']
    msg_id = msg['message_id']
    response = None

    if 'location' in msg:
        response = geocoder.request(lat=msg['location']['latitude'], lon=msg['location']['longitude'])
    elif 'text' in msg:
        # Geocoding from address string
        if hasnumbers.search(msg['text']):
            response = geocoder.request(q=msg['text'])
    else:
        tg.reply(chat_id, msg_id, _('watch.not_expected'), dialogue=True)

    response = geocoder.city_filter(response)

    if response is None:
        tg.reply(chat_id, msg_id, _('watch.blocked_or_broken'), dialogue=True)
        return
    elif len(response) > 1:
        multiple_choice(tg, chat_id, msg_id, response)
    elif len(response) == 1:
        add_watch(tg, chat_id, msg_id, geocoder.extract_streetname(response[0]))
    else:
        tg.reply(chat_id, msg_id, _('watch.wrong_address'), hide_keyboard=False, dialogue=True)


def multiple_choice(tg, chat_id, msg_id, response):
    kb = []
    for item in response:
        kb.append([geocoder.extract_streetname(item), ])

    tg.set_handler(chat_id, destiny_handler)
    tg.reply(chat_id, msg_id, _('watch.choose_your_destiny'), dialogue=True, reply_markup={'keyboard': kb})


def destiny_handler(tg, msg):
    chat_id = msg['chat']['id']
    msg_id = msg['message_id']
    tg.set_handler(chat_id, None)
    if 'text' in msg:
        add_watch(tg, chat_id, msg_id, msg['text'])
    else:
        tg.reply(chat_id, msg_id, _('watch.wat'), hide_keyboard=False, dialogue=True)


def add_watch(tg, chat_id, msg_id, address):
    cached_id = cached_address(address)
    if cached_id is None:
        tg.set_handler(chat_id, None)
        tg.reply(chat_id, msg_id, _('watch.blocked_or_broken'), hide_keyboard=True)
        return

    tg.set_handler(chat_id, None)
    result = subscribe(chat_id, cached_id)

    if result[0] is SubscribeStatus.already_watching:
        tg.reply(chat_id, msg_id, _('watch.already_watching'), hide_keyboard=True)
    elif result[0] is SubscribeStatus.done:
        tg.reply(chat_id, msg_id, _('watch.done'), hide_keyboard=True)
    elif result[0] is SubscribeStatus.done_with_blackouts:
        tg.reply(chat_id, msg_id, _('watch.done_with_blackouts') + result[1], hide_keyboard=True)

