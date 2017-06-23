import copy
from hashlib import md5

import redis
import requests
from celery import Celery
from lxml import html
from sqlalchemy import and_

import config
from bot import tg
from database import init_db, uses_db
from models import Blackout, BlackoutAddress, Subscribition, Address
from utils import format_blackout

celery = Celery('vloff_tasks', backend=config.CELERY_RESULT_BACKEND,
                broker=config.CELERY_BROKER_URL)
engine, db_session = init_db()

# http://loose-bits.com/2010/10/distributed-task-locking-in-celery.html
REDIS_CLIENT = redis.Redis()


def only_one(function=None, key="", timeout=None):
    """Enforce only one celery task at a time."""
    def _dec(run_func):
        def _caller(*args, **kwargs):
            ret_value = None
            have_lock = False
            lock = REDIS_CLIENT.lock(key, timeout=timeout)
            try:
                have_lock = lock.acquire(blocking=False)
                if have_lock:
                    ret_value = run_func(*args, **kwargs)
            finally:
                if have_lock:
                    lock.release()
            return ret_value
        return _caller
    return _dec(function) if function is not None else _dec


@celery.task(rate_limit=20, name='Send notification')
def send_notification(chat_id, text):
    tg.send_message(chat_id, text)


@uses_db(session=db_session)
def get_subscribitions(addresses_urls, session=None):
    subs_data = session.query(Subscribition, Address) \
        .join(Address, Subscribition.address_id == Address.id) \
        .join(BlackoutAddress, BlackoutAddress.address_url == Address.url) \
        .filter(BlackoutAddress.address_url.in_(addresses_urls))

    result = {}
    for sub in subs_data:
        chat_id = sub[0].chat
        if chat_id in result:
            result[chat_id].append((sub[1].address, sub[1].url))
        else:
            result[chat_id] = [(sub[1].address, sub[1].url)]
    return result


@celery.task(name='Notify add')
@uses_db(session=db_session)
def notify_add(addresses, blackout_id, session=None):
    subs = get_subscribitions(addresses)
    blackout = session.query(Blackout).get(blackout_id)
    for sub in subs:
        watchlist = subs[sub]
        text = _('notify.details')

        if len(subs[sub]) > 1:
            text = _('notify.details_multiple')

        formatted_text = format_blackout(text, subs[sub], blackout)
        send_notification.apply_async((sub, formatted_text))


@celery.task(name='Notify change')
@uses_db(session=db_session)
def notify_change(addresses, blackout_id, changes=[], session=None):
    if changes.count(True) == 0:
        return

    subs = get_subscribitions(addresses)
    blackout = session.query(Blackout).get(blackout_id)
    for sub in subs:
        watchlist = subs[sub]

        # These 'if' clauses are there so we can generate proper POT file with pygettext later
        text = ''
        if changes[4]:  # Actual again
            if len(subs[sub]) <= 1:
                text = _('notify.details_again')
            else:
                text = _('notify.details_again_multiple')

        elif changes.count(True) > 1:
            if len(subs[sub]) <= 1:
                text = _('notify.details_changed')
            else:
                text = _('notify.details_changed_multiple')

            text += '\n' + _('blackout.format_addressless')

        elif changes[0]:  # type
            if len(subs[sub]) <= 1:
                text = _('notify.type_changed')
            else:
                text = _('notify.type_changed_multiple')
        elif changes[1] or changes[2]:  # date/time
            if len(subs[sub]) <= 1:
                text = _('notify.time_changed')
            else:
                text = _('notify.time_changed_multiple')
        elif changes[3]:  # desc
            if len(subs[sub]) <= 1:
                text = _('notify.desc_changed')
            else:
                text = _('notify.desc_changed_multiple')

        formatted_text = format_blackout(text, subs[sub], blackout)
        send_notification.apply_async((sub, formatted_text))


@celery.task(name='Notify done')
@uses_db(session=db_session)
def notify_done(addresses, blackout_id, session=None):
    subs = get_subscribitions(addresses)
    blackout = session.query(Blackout).get(blackout_id)
    for sub in subs:
        watchlist = subs[sub]
        if len(subs[sub]) <= 1:
            text = _('notify.done')
        else:
            text = _('notify.done_multiple')

        formatted_text = format_blackout(text, subs[sub], blackout, accusative=True)
        send_notification.apply_async((sub, formatted_text))


def trim_time(inp):
    # vl.ru returns some weird symbols in time and date, so we need to remove them
    till = inp.find('по')
    if till == -1:
        return inp.strip()
    else:
        left = inp[:till].strip()
        right = inp[till:].strip()
        return left + ' ' + right


vlroot = 'http://www.vl.ru'


@celery.task(name='Parse addresses')
@uses_db(session=db_session)
def parse_addresses(blackout_id, checksum=None, changes=None, session=None):
    # Fetch addresses list for blackout
    blackout_link = vlroot + '/off/blackout/load-addresses/' + str(blackout_id)
    addresses_html = requests.get(blackout_link).content
    addresses_checksum = md5(addresses_html).hexdigest()

    registered_urls = []
    removed_urls = []
    addresses_changed = True

    if checksum is not None and addresses_checksum == checksum:
        addresses_changed = False

        # If even details are the same, then nothing has changed
        if True not in changes:
            return

    # Something has changed (in addresses list or blackout details), load all known affected addresses from db
    reg = session.query(BlackoutAddress).filter(BlackoutAddress.blackout_id == blackout_id).all()
    registered_urls = [a.address_url for a in reg]

    if addresses_changed:
        blackout = session.query(Blackout).get(blackout_id)
        blackout.addresses_checksum = addresses_checksum
        session.commit()

        removed_urls = copy.copy(registered_urls)  # Not deepcopy, as we won't change elements
        new_addresses = []
        addresses_root = html.fromstring(addresses_html)  # Parse addresses list
        for link in addresses_root.iterlinks():
            address_url = link[2]

            if address_url in registered_urls:
                removed_urls.remove(address_url)  # Address is still affected, no need to remove it now
            else:
                # Append suitable item for bulk_insert_mappings
                new_addresses.append({
                    'blackout_id': blackout_id, 'address_url': address_url
                })

        # Notify new affected addresses
        session.bulk_insert_mappings(BlackoutAddress, new_addresses)
        session.commit()
        new_addresses_list = [address['address_url'] for address in new_addresses]
        notify_add.apply_async((new_addresses_list, blackout_id))

    # Notify on changes. Note that newly affected addresses are not notified
    if changes and True in changes:
        notify_change.apply_async((registered_urls, blackout_id), {'changes': changes})

    if addresses_changed and removed_urls:
        # Notify those who are not affected anymore
        notify_done.apply_async((removed_urls, blackout_id))

        # And remove them from the db
        removed_sql_delete = BlackoutAddress.__table__.delete().where(
            and_(
                BlackoutAddress.blackout_id == blackout_id,
                BlackoutAddress.address_url.in_(removed_urls)
            )
        )
        session.execute(removed_sql_delete)
        session.commit()


@celery.task(name='Parse summary')
@only_one(key="ParseSummary", timeout=60 * 5)
@uses_db(session=db_session)
def parse_summary(session=None, **kwargs):
    summary_html = requests.get(vlroot + '/off/summary').content
    summary_root = html.fromstring(summary_html)
    blackouts = summary_root.xpath('//*[@id="resume"]/div/ul/li[contains(@class, \'blackout-item\')]')
    blackouts_ids = []

    for b in blackouts:
        blackout_type = b[0].text.strip()
        blackout_date = trim_time(b[1][0].text.strip())
        blackout_time = trim_time(b[1][1].text.strip())
        blackout_description = b[1][2].text.strip()[:-1]
        blackout_id = int(b[1][2][0].get('href').split('/')[-1].replace('.html', ''))
        blackouts_ids.append(blackout_id)

        checksum = None
        changes = [False, False, False, False, False]

        known_blackout = session.query(Blackout).get(blackout_id)
        if known_blackout:  # Detect changes and store them
            checksum = known_blackout.addresses_checksum

            if known_blackout.type_ != blackout_type:
                known_blackout.type_ = blackout_type
                changes[0] = True

            if known_blackout.date_ != blackout_date:
                known_blackout.date_ = blackout_date
                changes[1] = True

            if known_blackout.time_ != blackout_time:
                known_blackout.time_ = blackout_time
                changes[2] = True

            if known_blackout.description != blackout_description:
                known_blackout.description = blackout_description
                changes[3] = True

            if known_blackout.done == True:
                known_blackout.done = False
                changes[4] = True

            session.commit()
            session.flush()
        else:  # Register unknown blackout
            known_blackout = Blackout(id=blackout_id, type_=blackout_type, date_=blackout_date,
                                       time_=blackout_time, description=blackout_description)
            session.add(known_blackout)
            session.commit()
            session.flush()

        # For convenience, we notify on changes in parse_addresses
        parse_addresses.apply_async((blackout_id,), {'checksum': checksum, 'changes': changes})

    finished = session.query(Blackout).filter(~Blackout.id.in_(blackouts_ids), Blackout.done == False)
    finished_blackouts = []
    for b in finished:
        addresses = session.query(BlackoutAddress).filter(BlackoutAddress.blackout_id == b.id)
        addresses_list = [a.address_url for a in addresses]
        notify_done.apply_async((addresses_list, b.id))
        finished_blackouts.append(b)
    session.bulk_update_mappings(Blackout, [{'id': b.id, 'done': True} for b in finished_blackouts])
    session.commit()


@celery.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(60.0 * 5.0, parse_summary, name='monitor vl.ru/off')
    #parse_summary.apply_async()