def initialize(bot):
    bot.register_command('/help', help_command)
    bot.register_handler(help_command)


def help_command(bot, msg):
    bot.send_message(msg['chat']['id'], _('help.line_1'))
