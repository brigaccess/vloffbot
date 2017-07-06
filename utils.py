from enum import Enum

from database import uses_db
from models import Address, Blackout, BlackoutAddress, Subscribition


def get_genitive(s):
    if s == 'Горячая вода':
        return 'Горячей воды'
    elif s == 'Холодная вода':
        return 'Холодной воды'
    elif s == 'Электричество':
        return 'Электричества'
    elif s == 'Отопление':
        return 'Отопления'


def get_accusative(s):
    if s == 'Горячая вода':
        return 'Горячую воду'
    elif s == 'Холодная вода':
        return 'Холодную воду'
    elif s == 'Электричество':
        return 'Электричество'
    elif s == 'Отопление':
        return 'Отопление'


def get_emoji(s):
    if s == 'Горячая вода':
        return '🔴'
    elif s == 'Холодная вода':
        return '🔵'
    elif s == 'Электричество':
        return '💡'
    elif s == 'Отопление':
        return '🔥'


def format_blackout(s, addresses, blackout, nominative=False, accusative=False):
    if not accusative:
        type_capitalized = get_genitive(blackout.type_)
    else:
        type_capitalized = get_accusative(blackout.type_)
    type = type_capitalized.lower()

    return s.format(
            addresses=format_addresses(addresses), id=blackout.id,
            url='http://www.vl.ru/off/blackout/%d.html?utm_source=vloffbot' % blackout.id,
            date=blackout.date_, time=blackout.time_, desc=blackout.description.strip(),
            type=type, type_capitalized=type_capitalized, type_emoji=get_emoji(blackout.type_),
            type_nominative = blackout.type_.lower(), type_nominative_capitalized = blackout.type_
            )


def format_addresses(addresses):
    result = ''
    if len(addresses) > 1:
        result = ''
        for address in addresses:
            result += '[- %s](http://www.vl.ru%s?utm_source=vloffbot)\n' % address
    elif len(addresses) == 1:
        result = '[%s](http://www.vl.ru%s?utm_source=vloffbot)' % addresses[0]
    return result


class SubscribeStatus(Enum):
    already_watching = 1
    done = 2
    done_with_blackouts = 3


@uses_db
def subscribe(chat_id, address_id, session=None):
    if session.query(Subscribition).filter(Subscribition.chat == chat_id,
                                           Subscribition.address_id == address_id).count() > 0:
        return SubscribeStatus.already_watching, None

    w = Subscribition(chat=chat_id, address_id=address_id)
    session.add(w)
    session.commit()

    current_blackouts = session.query(Address, Blackout) \
        .join(BlackoutAddress, Address.url == BlackoutAddress.address_url) \
        .join(Blackout, BlackoutAddress.blackout_id == Blackout.id) \
        .filter(Address.id == address_id, Blackout.done == False)

    result_text = ''

    for item in current_blackouts:
        result_text += '\n'
        result_text += format_blackout(_('blackout.format_addressless'), [(item[0].address, item[0].url)], item[1])

    if len(result_text) > 0:
        return SubscribeStatus.done_with_blackouts, result_text
    else:
        return SubscribeStatus.done, None