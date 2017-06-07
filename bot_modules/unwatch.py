from database import uses_db
from models import Subscribition, Address


def initialize(tg):
    tg.register_command('/unwatch', unwatch_command)


@uses_db
def unwatch_command(tg, msg, session=None):
    chat_id = msg['chat']['id']
    watches = session.query(Subscribition, Address).join(Address, Subscribition.address_id == Address.id)\
        .filter(Subscribition.chat == chat_id)
    if watches.count() > 1:
        kb = []
        for watch in watches:
            kb.append([watch[1].address, ])
        kb.append([_('unwatch.cancel'), ])

        tg.set_handler(chat_id, unwatch_listener)
        tg.send_message(chat_id, _('unwatch.choose_wisely'), reply_markup={'keyboard': kb})
    elif watches.count() == 1:
        w = watches.first()[0]
        session.delete(w)
        session.commit()
        tg.send_message(chat_id, _('unwatch.removed'))
    else:
        tg.send_message(chat_id, _('unwatch.nothing_to_unwatch'))


@uses_db
def unwatch_listener(tg, msg, session=None):
    chat_id = msg['chat']['id']
    if 'text' in msg:
        if msg['text'] == _('unwatch.cancel'):
            tg.set_handler(chat_id, None)
            tg.send_message(chat_id, _('main.cancelled'))
            return

        w = session.query(Subscribition).join(Address, Subscribition.address).filter(
            Subscribition.chat == chat_id, Address.address == msg['text']
        ).one_or_none()
        if w:
            session.delete(w)
            session.commit()
            tg.set_handler(chat_id, None)
            tg.send_message(chat_id, _('unwatch.removed'))
        else:
            tg.send_message(chat_id, _('unwatch.not_found'), hide_keyboard=False)
    else:
        tg.send_message(chat_id, _('unwatch.aaaargh'))

