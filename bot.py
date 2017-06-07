import gettext
import json
import logging
import sys
import traceback
import requests

import config
import telegram
from bot_modules import *

gettext.translation('offnotificationbot', './locale/', languages=['ru_RU']).install()

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(name)-15s %(levelname)-8s %(message)s')

logging.info('Initializing Telegram API...')
tg = telegram.Telegram(config.API_KEY)
logging.info('Initialized')

if __name__ == '__main__':
    for submodule in dir(sys.modules['bot_modules']):
        if submodule.startswith('_'):
            continue
        else:
            m = sys.modules['bot_modules.' + submodule]
            try:
                getattr(m, 'initialize')(tg)
            except AttributeError as e:
                logging.debug('Module ' + submodule + ' has no initialize(tg)')  # No init method? No problem

    offset = 0
    timeout = 60
    while True:
        try:
            r = requests.get('https://api.telegram.org/bot%s/getUpdates?offset=%s&timeout=%s' % (config.API_KEY, offset, timeout),
                             timeout=timeout-1)
            if r.content:
                for update in r.json()['result']:
                    try:
                        tg.process_update(update)
                    except Exception as e:
                        log = traceback.format_exc()
                        traceback.print_exc()
                        crashed_chat = update['message']['chat']['id']

                        tg.send_message(
                            update['message']['chat']['id'],
                            _('kirov.reporting'),
                            reply_to_message_id=update['message']['message_id'])

                        sent_trace = tg.send_message(
                            config.ERROR_REPORTS_CHAT,
                            '```\nUPDATE ' + str(update['update_id']) + '\n' + log + '\n```',
                            parse_mode='Markdown'
                        )
                        tg.send_document(
                            config.ERROR_REPORTS_CHAT,
                            str(update['update_id']) + '.txt',
                            json.dumps(update, indent=4),
                            'text/plain',
                            reply_to_message_id=sent_trace['result']['message_id']
                        )

                    offset = update['update_id'] + 1
                    logging.debug(update)
        except Exception as e:
            traceback.print_exc()
