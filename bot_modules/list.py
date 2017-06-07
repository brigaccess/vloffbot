from database import uses_db
from models import Subscribition, Blackout, BlackoutAddress, Address
from utils import format_blackout


def initialize(tg):
    tg.register_command('/list', list_command)


@uses_db
def list_command(tg, msg, session=None):
    chat_id = msg['chat']['id']
    msg_id = msg['message_id']
    subs = session.query(Subscribition).filter(Subscribition.chat == chat_id)
    if subs.count() == 0:
        tg.reply(chat_id, msg_id, _('status.nothing_is_watched'))
        return
    result_text = _('list.addresses_you_watch')
    for sub in subs:
        result_text += '\n' + sub.address.address

    tg.reply(chat_id, msg_id, result_text)
