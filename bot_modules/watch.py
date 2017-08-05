import json
import re

from address_cache import cached_address
from utils import subscribe, SubscribeStatus
import geocoder

hasnumbers = re.compile('[0-9]')


def initialize(bot):
    bot.register_command('/watch', watch_command)


def watch_command(bot, msg):
    chat_id = msg['chat']['id']
    msg_id = msg['message_id']
    bot.set_handler(chat_id, address_handler)
    bot.reply(chat_id, msg_id, _('watch.welcome'), dialogue=True)


def address_handler(bot, msg):
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
        bot.reply(chat_id, msg_id, _('watch.not_expected'), dialogue=True)

    response = geocoder.city_filter(response)

    if response is None:
        bot.reply(chat_id, msg_id, _('watch.blocked_or_broken'), dialogue=True)
        return
    elif len(response) > 1:
        multiple_choice(bot, chat_id, msg_id, response)
    elif len(response) == 1:
        add_watch(bot, chat_id, msg_id, geocoder.extract_streetname(response[0]))
    else:
        bot.reply(chat_id, msg_id, _('watch.wrong_address'), hide_keyboard=False, dialogue=True)


def multiple_choice(bot, chat_id, msg_id, response):
    kb = []
    for item in response:
        kb.append([geocoder.extract_streetname(item), ])

    bot.set_handler(chat_id, destiny_handler)
    bot.send_keyboard(chat_id, _('watch.choose_your_destiny'), kb, dialogue=True, msg_id=msg_id)


def destiny_handler(bot, msg):
    chat_id = msg['chat']['id']
    msg_id = msg['message_id']
    bot.set_handler(chat_id, None)
    if 'text' in msg:
        add_watch(bot, chat_id, msg_id, msg['text'])
    else:
        bot.reply(chat_id, msg_id, _('watch.wat'), hide_keyboard=False, dialogue=True)


def add_watch(bot, chat_id, msg_id, address):
    cached_id = cached_address(address)
    if cached_id is None:
        bot.set_handler(chat_id, None)
        bot.reply(chat_id, msg_id, _('watch.blocked_or_broken'), hide_keyboard=True)
        return

    bot.set_handler(chat_id, None)
    result = subscribe(chat_id, cached_id)

    if result[0] is SubscribeStatus.already_watching:
        bot.reply(chat_id, msg_id, _('watch.already_watching'), hide_keyboard=True)
    elif result[0] is SubscribeStatus.done:
        bot.reply(chat_id, msg_id, _('watch.done'), hide_keyboard=True)
    elif result[0] is SubscribeStatus.done_with_blackouts:
        bot.reply(chat_id, msg_id, _('watch.done_with_blackouts') + result[1], hide_keyboard=True)

