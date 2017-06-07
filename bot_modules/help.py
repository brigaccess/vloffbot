def initialize(tg):
    tg.register_command('/help', help_command)


def help_command(tg, msg):
    tg.send_message(msg['chat']['id'], _('help.line_1'))
