from database import uses_db
from models import Subscribition, Blackout, BlackoutAddress, Address
from utils import format_addresses


def initialize(bot):
    bot.register_command('/list', list_command)
    bot.register_handler(list_command)


@uses_db
def list_command(bot, msg, session=None):
    chat_id = msg['chat']['id']
    msg_id = msg['message_id']
    subs = session.query(Subscribition, Address)\
        .join(Address, Subscribition.address_id == Address.id)\
        .filter(Subscribition.chat == chat_id)
    if subs.count() == 0:
        bot.reply(chat_id, msg_id, _('status.nothing_is_watched'))
        return

    result_text = _('list.addresses_you_watch')
    result_text += format_addresses([(item[1].address, item[1].url) for item in subs], msg['markdown_supported'])

    bot.reply(chat_id, msg_id, result_text)
