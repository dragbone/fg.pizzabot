import plugins
import pizzaparser
from operator import add

MEM_NAME = "pizzavotes"


def _initialise(bot):
    plugins.register_user_command(["vote", "pizza"])
    plugins.register_admin_command(["resetvotes", "dumpvotes"])


indexToDay = {0:"Monday",
              1:"Tuesday",
              2:"Wednesday",
              3:"Thursday",
              4:"Friday"}

def pizza(bot, event, *args):
    initMemory(bot)

    votes = [0] * 5
    mvotes = bot.memory.get_by_path([MEM_NAME])  # grab all votes
    for user_id in mvotes:
        vote = mvotes[user_id]
        votes = list(map(add, votes, vote))

    indices = [i for i, x in enumerate(votes) if x == max(votes)]
    days = list(map(lambda x:indexToDay[x], indices))
    yield from bot.coro_send_message(event.conv, _("Pizzaday could be on {}").format(days))

    recommendedDay = indexToDay[pizzaparser.choosePizzaDay(indices)]
    yield from bot.coro_send_message(event.conv, _("I recommend to eat pizza on {}").format(recommendedDay))

def dumpvotes(bot, event, *args):
    initMemory(bot)

    mvotes = bot.memory.get_by_path([MEM_NAME])  # grab all votes
    for user_id in mvotes:
        vote = mvotes[user_id]
        yield from bot.coro_send_message(event.conv, _("Vote for " + user_id + ": {}").format(vote))

def initMemory(bot):
    if not bot.memory.exists([MEM_NAME]):
        bot.memory.set_by_path([MEM_NAME], {})
        bot.memory.save()

def resetvotes(bot, event, *args):
    initMemory(bot)

    counter = 0
    bot.memory.set_by_path([MEM_NAME], {})
    bot.memory.save()
    yield from bot.coro_send_message(event.conv, _("Deleted {} vote(s)").format(counter))

def vote(bot, event, *args):
    initMemory(bot)

    if not args:
        yield from bot.coro_send_message(event.conv, _("Usage: /bot vote <i>Mon-Wed,(Fri)</i>\n/bot vote {}"))
        return

    try:
        vote = pizzaparser.parsePizzaVote(args)
        bot.memory.set_by_path([MEM_NAME, event.user.id_.chat_id], vote)
        bot.memory.save()
        yield from bot.coro_send_message(event.conv, _("Thank you for voting ({})").format(vote))
    except Exception as ex:
        yield from bot.coro_send_message(event.conv, _("Error: Do you even syntax?! " + ex))
