import plugins
import random

def _initialise(bot):
    plugins.register_user_command(["pizza"])

def pizza(bot, event, *args):
    """
    Selects random pizza day

    /bot pizza <i>'option1' 'option2'</i>
    """

    if not args:
        yield from bot.coro_send_message(event.conv, _("Usage: /bot pizza <i>Mon Tue Sat</i>"))
        return

    try:
        yield from bot.coro_send_message(event.conv, _("Pizza day shall be on {}").format(random.choice(args)))
    except ValueError:
        yield from bot.coro_send_message(event.conv, _("Error: You suck."))
