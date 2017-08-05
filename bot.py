import gettext
import logging
import multiprocessing as mp
import sys
import traceback

from bot_modules import *
from messengers import *
from database import uses_db
from models import Chat

gettext.translation('offnotificationbot', './locale/', languages=['ru_RU']).install()

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(name)-15s %(levelname)-8s %(message)s')


class Bot:
    logger = None
    messengers = {}
    commands = {}
    handlers = {}
    active_calls = {}
    queue = None

    def __init__(self):
        self.logger = logging.getLogger(name='Bot')

    def loop(self):
        # Start messengers processes
        self.queue = mp.Queue()
        for messenger in self.messengers:
            try:
                m = self.messengers[messenger]
                gu = getattr(m, 'get_updates')
                process = mp.Process(target=gu, args=(self.queue, ))
                process.start()
                print(process)
            except AttributeError as e:
                self.logger.warning('Messenger ' + messenger + ' has no get_updates(q) loop')
                traceback.print_exc()
                continue
            except Exception as e:
                traceback.print_exc()
        while True:
            update = self.queue.get(True)
            self.process_update(update)

    @staticmethod
    def command_check(chat_id, text):
        return text.startswith('/')

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
                call = self.active_calls[chat_id]
                self.logger.debug('%s has assigned handler %s.%s' % (chat_id, call['module'], call['method']))
                if call['module'] not in sys.modules:
                    # TODO Send a message that says that the command is not available
                    self.logger.warning('%s handler module is unavailable' % (chat_id))
                    del self.active_calls[chat_id]
                    return
                call_module = sys.modules[call['module']]
                try:
                    method = getattr(call_module, call['method'])
                except AttributeError as e:
                    self.logger.warning('%s handler module \'%s\' has no method \'%s\'!',
                                        (chat_id, call['module'], call['method']))
                    del self.active_calls[chat_id]
                    return
                if method:
                    args = []
                    kwargs = {}
                    if 'args' in call and isinstance(call['args'], type(list)):
                        args = call['args']
                    if 'kwargs' in call and isinstance(call['kwargs'], type(dict)):
                        kwargs = call['kwargs']

                method(self, msg, *self.active_calls[chat_id]['args'], **kwargs)

            # New command request
            elif 'text' in msg and self.command_check(chat_id, msg['text']):
                self.logger.debug('%s requested a command %s' % (chat_id, msg['text']))
                self.execute_command(msg)

            # The bot was added to a new chat
            elif 'bot_added' in msg:
                chat_data.added = msg['from']['id']
                self.execute_command(msg, command='/start')
                self.logger.info('New chat: ' + str(chat_id) + ' ' + msg['chat']['title'])

            # The bot was kicked
            elif 'bot_kicked' in msg:
                chat_data.active = False
                self.logger.info('Kicked from chat: ' + str(chat_id) + ' ' + msg['chat']['title'])

            # Chat was transformed to a supergroup
            elif 'migrate_to_chat_id' in msg:
                session.delete(session.query(Chat).get(msg['migrate_to_chat_id']))
                chat_data.id = msg['migrate_to_chat_id']
            session.commit()

    def resolve_id(self, chat_id):
        return self.messengers[chat_id[0:2]], chat_id[2:]

    def send_message(self, chat_id, text, hide_keyboard=None, dialogue=False, **kwargs):
        messenger, original_chat_id = self.resolve_id(chat_id)
        messenger.send_message(original_chat_id, text, hide_keyboard=hide_keyboard, dialogue=dialogue, **kwargs)

    def send_keyboard(self, chat_id, text, keyboard, one_time=True, dialogue=False, msg_id=None):
        messenger, original_chat_id = self.resolve_id(chat_id)
        messenger.send_keyboard(original_chat_id, text, keyboard, one_time=one_time, dialogue=dialogue, msg_id=msg_id)

    def reply(self, chat_id, msg_id, text, **kwargs):
        messenger, original_chat_id = self.resolve_id(chat_id)
        r = None
        try:
            r = getattr(messenger, 'reply')
        except AttributeError as e:
            pass
        except:
            traceback.print_exc()
        if r is None:  # Messenger doesn't support any form of replies
            messenger.send_message(original_chat_id, msg_id, text, **kwargs)
        else:
            r(original_chat_id, msg_id, text, **kwargs)

    def register_messenger(self, name, messenger):
        self.messengers[name] = messenger
        self.logger.info('Registered messenger ' + name + ' (' + str(messenger) + ')')

    def register_command(self, cmd, handler):
        self.commands[cmd] = handler
        self.logger.info('Registered command ' + cmd + ' with handler ' + str(handler))

    def register_callback(self, t, handler):
        self.callback_handlers[t] = handler
        self.logger.info('Registered callback handler ' + str(handler) + ' for type ' + t)

    def set_handler(self, chat_id, handler, *args, **kwargs):
        if handler is not None:
            self.active_calls[chat_id] = {'module': handler.__module__, 'method': handler.__name__,
                                          'args': args, 'kwargs': kwargs}
            # TODO Persist
        else:
            if chat_id in self.active_calls:
                del self.active_calls[chat_id]


if __name__ == '__main__':
    bot = Bot()
    for submodule in dir(sys.modules['messengers']):
        if submodule.startswith('_'):
            continue
        else:
            m = sys.modules['messengers.' + submodule]
            try:
                result = getattr(m, 'initialize')()
                bot.register_messenger(result.get_name(result), result)
            except AttributeError as e:
                logging.error('Module ' + submodule + ' has no initialize() or returned object have no get_name()')

    for submodule in dir(sys.modules['bot_modules']):
        if submodule.startswith('_'):
            continue
        else:
            m = sys.modules['bot_modules.' + submodule]
            try:
                getattr(m, 'initialize')(bot)
            except AttributeError as e:
                logging.debug('Module ' + submodule + ' has no initialize(bot)')  # No init method? No problem
    bot.loop()
