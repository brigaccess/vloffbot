from database import uses_db
from models import Subscribition, Address


def initialize(bot):
    bot.register_command('/unwatch', unwatch_command)


@uses_db
def unwatch_command(bot, msg, session=None):
    chat_id = msg['chat']['id']
    msg_id = msg['message_id']
    watches = session.query(Subscribition, Address).join(Address, Subscribition.address_id == Address.id)\
        .filter(Subscribition.chat == chat_id)
    if watches.count() > 1:
        kb = []
        for watch in watches:
            kb.append([watch[1].address, ])
        kb.append([_('unwatch.cancel'), ])

        bot.set_handler(chat_id, unwatch_listener)
        bot.send_keyboard(chat_id, _('unwatch.choose_wisely'), kb, dialogue=True, msg_id=msg_id)
    elif watches.count() == 1:
        w = watches.first()[0]
        session.delete(w)
        session.commit()
        bot.reply(chat_id, msg_id, _('unwatch.removed'))
    else:
        bot.reply(chat_id, msg_id, _('unwatch.nothing_to_unwatch'))


@uses_db
def unwatch_listener(bot, msg, session=None):
    chat_id = msg['chat']['id']
    msg_id = msg['message_id']
    if 'text' in msg:
        if msg['text'] == _('unwatch.cancel'):
            bot.set_handler(chat_id, None)
            bot.reply(chat_id, msg_id, _('main.cancelled'), hide_keyboard=True)
            return

        w = session.query(Subscribition).join(Address, Subscribition.address).filter(
            Subscribition.chat == chat_id, Address.address == msg['text']
        ).one_or_none()
        if w:
            session.delete(w)
            session.commit()
            bot.set_handler(chat_id, None)
            bot.reply(chat_id, msg_id, _('unwatch.removed'), hide_keyboard=True)
        else:
            bot.reply(chat_id, msg_id, _('unwatch.not_found'), dialogue=True)
    else:
        bot.reply(chat_id, msg_id, _('unwatch.aaaargh'), dialogue=True)

