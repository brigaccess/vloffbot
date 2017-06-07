from database import uses_db
from models import Chat


def initialize(tg):
    tg.register_command('/start', start_command)


@uses_db
def start_command(tg, msg, session=None):
    chat_id = msg['chat']['id']
    chat_data = session.query(Chat).filter(Chat.id == chat_id).first()
    if chat_data is not None:
        chat_data.active = True
        session.commit()

    tg.send_message(chat_id, _('help.line_1'))
