import json
import logging
import requests

from database import uses_db
from models import Chat


class Telegram:
    active_calls = {}
    commands = {}
    callback_handlers = {}
    bot_info = None
    logger = None
    api_logger = None
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

    def request_bot_info(self):
        response = self.api_call('getMe')
        if 'ok' in response and response['ok']:
            self.bot_info = response['result']
        else:
            raise Exception('getMe: Telegram API answered with ' + str(response))

    @staticmethod
    def command_check(chat_id, text):
        return text.startswith('/')

    @uses_db
    def process_update(self, update, session=None):
        self.logger.debug('Started processing the update ' + str(update))
        if 'message' in update:
            msg = update['message']
            chat_id = msg['chat']['id']

            chat_data = session.query(Chat).filter(Chat.id == chat_id).first()
            if chat_data is None:
                self.logger.debug('Unknown chat. Registering...')
                chat_data = Chat(id=chat_id)
                session.add(chat_data)
                session.commit()
                self.logger.debug('Commited')

            # Ignore pin updates
            if 'pinned_message' in msg:
                pass

            # /cancel
            elif 'text' in msg and self.command_check(chat_id, msg['text']) and msg['text'].startswith('/cancel'):
                self.set_handler(chat_id, None)
                self.send_message(chat_id, _('main.cancelled'))

            # Answer to previously requested command
            elif chat_id in self.active_calls:
                self.logger.debug('%s has assigned handler %s' % (chat_id, self.active_calls[chat_id]))
                self.active_calls[chat_id](self, msg)

            # New command request
            elif 'text' in msg and self.command_check(chat_id, msg['text']):
                self.logger.debug('%s requested a command %s' % (chat_id, msg['text']))
                self.execute_command(msg)

            # The bot was added to a new chat
            elif 'new_chat_member' in msg and msg['new_chat_member']['id'] == self.bot_info['id']:
                chat_data.added = msg['from']['id']
                self.execute_command(msg, command='/start')
                self.logger.info('New chat: ' + str(chat_id) + ' ' + msg['chat']['title'])

            # The bot was kicked
            elif 'left_chat_member' in msg and msg['left_chat_member']['id'] == self.bot_info['id']:
                chat_data.active = False
                self.logger.info('Kicked from chat: ' + str(chat_id) + ' ' + msg['chat']['title'])

            # Chat was transformed to a supergroup
            elif 'migrate_to_chat_id' in msg:
                session.delete(session.query(Chat).get(msg['migrate_to_chat_id']))
                chat_data.id = msg['migrate_to_chat_id']
            session.commit()

    def api_call(self, method, args={}, **kwargs):
        self.api_logger.info('Calling method %s with %s' % (method, args))

        args.update(kwargs)
        response = requests.post(self._API_PATH + method, data=args)

        self.api_logger.debug('Answer: %s' % response.json())
        return response.json()

    def execute_command(self, msg, command=None):
        fake_msg = msg

        if command is None:
            command = msg['text'].split('@', 1)[0].split(' ', 1)[0]
        else:
            fake_msg['text'] = command

        if command in self.commands:
            self.commands[command](self, fake_msg)
        else:
            self.send_message(fake_msg['chat']['id'], _('main.unknown_command'))

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

    def reply(self, chat_id, msg_id, text, **kwargs):
        return self.send_message(chat_id, text, reply_to_message_id=msg_id, **kwargs)

    def send_document(self, chat_id, name, document, mime, reply_markup=None, **kwargs):
        return self.api_call('sendDocument', {'chat_id': chat_id}, files={'document': (name, document, mime)}, **kwargs)

    def register_command(self, cmd, handler):
        self.commands[cmd] = handler
        self.logger.info('Registered command ' + cmd + ' with handler ' + str(handler))

    def register_callback(self, t, handler):
        self.callback_handlers[t] = handler
        self.logger.info('Registered callback handler ' + str(handler) + ' for type ' + t)

    def set_handler(self, chat_id, handler):
        if handler is not None:
            self.active_calls[chat_id] = handler
        else:
            if chat_id in self.active_calls:
                del self.active_calls[chat_id]
