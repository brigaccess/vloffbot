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

