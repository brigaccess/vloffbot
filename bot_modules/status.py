from database import uses_db
from models import Subscribition, Blackout, BlackoutAddress, Address
from utils import format_blackout


def initialize(tg):
    tg.register_command('/status', status_command)


@uses_db
def status_command(tg, msg, session=None):
    chat_id = msg['chat']['id']
    msg_id = msg['message_id']
    subs = session.query(Subscribition).filter(Subscribition.chat == chat_id).count()
    if subs == 0:
        tg.reply(chat_id, msg_id, _('status.nothing_is_watched'))
        return

    current_status = session.query(Address, Blackout)\
        .join(Subscribition, Address.id == Subscribition.address_id)\
        .join(BlackoutAddress, Address.url == BlackoutAddress.address_url)\
        .join(Blackout, BlackoutAddress.blackout_id == Blackout.id)\
        .filter(Subscribition.chat == chat_id, Blackout.done == False)

    if current_status.count() == 0:
        tg.reply(chat_id, msg_id, _('status.no_blackouts'))
        return

    result_text = _('status.current_blackouts')
    for item in current_status:
        item_text = '\n\n' + _('blackout.format')
        result_text += format_blackout(item_text, item[0], item[1])
    tg.reply(chat_id, msg_id, result_text)
