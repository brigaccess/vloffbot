import gettext
import json
import logging
import requests
import sys
import traceback

import config
from database import uses_db
from models import Chat


def initialize():
    return Telegram(config.API_KEY)


class Telegram:
    bot_info = None
    logger = None
    api_logger = None
    timeout = 60
    offset = 0

    keyboard_options = {
        'resize_keyboard': True,
        'force_reply': True
    }
    hide_keyboard = {
        'hide_keyboard': True
    }
    force_reply = {
        'force_reply': True
    }

    def __init__(self, key):
        self._KEY = key
        self._API_PATH = 'https://api.telegram.org/bot%s/' % key
        self._FILE_PATH = 'https://api.telegram.org/file/bot%s/' % key
        self.logger = logging.getLogger(name='Telegram')
        self.api_logger = logging.getLogger('TelegramAPI')
        self.request_bot_info()

    @staticmethod
    def get_name(self):
        return 'tg'

    def request_bot_info(self):
        response = self.api_call('getMe')
        if 'ok' in response and response['ok']:
            self.bot_info = response['result']
        else:
            raise Exception('getMe: Telegram API answered with ' + str(response))

    def api_call(self, method, args={}, **kwargs):
        self.api_logger.info('Calling method %s with %s' % (method, args))

        args.update(kwargs)
        response = requests.post(self._API_PATH + method, data=args)

        self.api_logger.debug('Answer: %s' % response.json())
        return response.json()

    def send_message(self, chat_id, text, hide_keyboard=None, dialogue=False, **kwargs):
        argsdict = {'chat_id': chat_id, 'text': text, 'disable_notification': True, 'disable_web_page_preview': True,
                    'parse_mode': 'Markdown'}
        argsdict.update(kwargs)

        if 'reply_markup' in argsdict and type(argsdict['reply_markup']) != str:
            if 'keyboard' in argsdict['reply_markup']:
                argsdict['reply_markup'].update(self.keyboard_options)
            argsdict['reply_markup'] = json.dumps(argsdict['reply_markup'])

        elif 'reply_markup' not in argsdict:
            options = {}
            if hide_keyboard:
                options.update(self.hide_keyboard)
            if dialogue:
                options.update(self.force_reply)
            argsdict['reply_markup'] = json.dumps(options)

        return self.api_call('sendMessage', argsdict)

    def send_keyboard(self, chat_id, text, keyboard, one_time=True, dialogue=False, msg_id=None):
        if dialogue and msg_id is not None:
            self.reply(chat_id, msg_id, text, reply_markup={'keyboard': keyboard})
        else:
            self.send_message(chat_id, msg_id, text, reply_markup={'keyboard': keyboard})

    def reply(self, chat_id, msg_id, text, **kwargs):
        return self.send_message(chat_id, text, reply_to_message_id=msg_id, **kwargs)

    def send_document(self, chat_id, name, document, mime, reply_markup=None, **kwargs):
        return self.api_call('sendDocument', {'chat_id': chat_id}, files={'document': (name, document, mime)}, **kwargs)

    def get_updates(self, q):
        self.logger.info('get_updates loop started')
        while True:
            try:
                r = requests.get('https://api.telegram.org/bot%s/getUpdates?offset=%s&timeout=%s' %
                                 (config.API_KEY, self.offset, self.timeout), timeout=self.timeout - 1)
                if r.content:
                    for update in r.json()['result']:
                        try:
                            if 'message' in update:
                                update['message']['from']['id'] = 'tg' + str(update['message']['chat']['id'])
                                update['message']['chat']['id'] = 'tg' + str(update['message']['chat']['id'])
                                update['message']['markdown_supported'] = False

                            if 'new_chat_member' in update and update['new_chat_member']['id'] == self.bot_info['id']:
                                del update['new_chat_member']
                                update['bot_added'] = True

                            if 'left_chat_member' in update and update['left_chat_member']['id'] == self.bot_info['id']:
                                del update['left_chat_member']
                                update['bot_kicked'] = True

                            if 'migrate_to_chat_id' in update:
                                update['migrate_to_chat_id'] = 'tg' + str(update['migrate_to_chat_id'])

                            q.put(update)
                        except Exception as e:
                            log = traceback.format_exc()
                            traceback.print_exc()
                            crashed_chat = update['message']['chat']['id']

                            self.send_message(
                                update['message']['chat']['id'],
                                _('kirov.reporting'),
                                reply_to_message_id=update['message']['message_id'])

                            sent_trace = self.send_message(
                                config.ERROR_REPORTS_CHAT,
                                '```\nTG UPDATE ' + str(update['update_id']) + '\n' + log + '\n```',
                                parse_mode='Markdown'
                            )

                            self.send_document(
                                config.ERROR_REPORTS_CHAT,
                                str(update['update_id']) + '.txt',
                                json.dumps(update, indent=4),
                                'text/plain',
                                reply_to_message_id=sent_trace['result']['message_id']
                            )

                        self.offset = update['update_id'] + 1
                        logging.debug(update)
            except Exception as e:
                traceback.print_exc()