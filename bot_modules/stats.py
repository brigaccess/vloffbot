from database import uses_db
from datetime import datetime, timedelta
from models import Chat, Subscribition


def initialize(tg):
    tg.register_command('/stats', stats_command)


@uses_db
def stats_command(tg, msg, session=None):
    user_id = msg['from']['id']
    user = session.query(Chat).get(user_id)
    if user and user.admin == True:
        text = _('stats.details')
        limits = [datetime.today() - timedelta(days=1), datetime.today() - timedelta(days=7),
                  datetime.today() - timedelta(days=30), datetime.fromtimestamp(0)]

        results = []
        for limit in limits:
            results.append([
                session.query(Chat).filter(Chat.id >= 0, Chat.added_on >= limit).count(),
                session.query(Chat).filter(Chat.id < 0, Chat.added_on >= limit).count(),
                session.query(Subscribition).filter(
                    Subscribition.chat >= 0,
                    Subscribition.added_on >= limit
                ).count(),
                session.query(Subscribition).filter(
                    Subscribition.chat < 0,
                    Subscribition.added_on >= limit
                ).count(),
                session.query(Chat).outerjoin(Subscribition, Chat.id == Subscribition.chat).filter(
                    Subscribition.chat == None, Chat.id >= 0, Chat.added_on >= limit
                ).count(),
                session.query(Chat).outerjoin(Subscribition, Chat.id == Subscribition.chat).filter(
                    Subscribition.chat == None, Chat.id < 0, Chat.added_on >= limit
                ).count(),
            ])
        text = text.format(daily=results[0], weekly=results[1], monthly=results[2], total=results[3])

        tg.send_message(msg['chat']['id'], text)
    else:
        tg.send_message(msg['chat']['id'], _('main.unknown_command'))