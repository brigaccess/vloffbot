import base64
import traceback
from binascii import Error

import address_cache
from database import uses_db
from models import Address, Chat
from utils import subscribe, SubscribeStatus


def initialize(bot):
    bot.register_command('/start', start_command)


@uses_db
def start_command(bot, msg, session=None):
    chat_id = msg['chat']['id']
    chat_data = session.query(Chat).filter(Chat.id == chat_id).first()
    if chat_data is not None:
        chat_data.active = True
        session.commit()

    arguments = msg['text'].split(' ')[1:]
    if len(arguments) == 1:
        start_with_address(bot, msg, arguments)
    else:
        bot.send_message(chat_id, _('help.line_1'))


@uses_db
def start_with_address(bot, msg, arguments, session=None):
    chat_id = msg['chat']['id']
    try:
        b64address = base64.b64decode(arguments[0]).decode("utf-8")
        cached_address = address_cache.add_address_from_url(b64address)
        if cached_address is not None:
            address = session.query(Address).get(cached_address)
            result = subscribe(chat_id, cached_address)
            if result[0] is SubscribeStatus.already_watching:
                bot.send_message(chat_id, _('watch.already_watching'), hide_keyboard=True)
            elif result[0] is SubscribeStatus.done:
                bot.send_message(chat_id, _('start.done').format(addresses=address.address), hide_keyboard=True)
            elif result[0] is SubscribeStatus.done_with_blackouts:
                bot.send_message(chat_id, _('start.done_with_blackouts').format(addresses=address.address) + result[1],
                                hide_keyboard=True)
            return
    except Error as e:
        pass
    except Exception as e:
        traceback.print_exc()
    bot.send_message(chat_id, _('help.line_1'))