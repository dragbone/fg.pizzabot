import plugins
import random
from operator import add

def _initialise(bot):
    plugins.register_user_command(["vote", "pizza"])
    plugins.register_admin_command(["resetvotes","dumpvotes"])


indexToDay = {0:"Monday",
              1:"Tuesday",
              2:"Wednesday",
              3:"Thursday",
              4:"Friday"}

dayToIndex = {"mo":0,
              "di":1, "tu":1,
              "mi":2, "we":2,
              "do":3, "th":3,
              "fr":4}

validDays = [0,1,2,3,4]

noVote = ["none", "null", "{}", "()", "nada", "never"]

def pizza(bot, event, *args):
    initMemory(bot)

    votes = [0] * 5
    mvotes = bot.memory.get_by_path(["pizzavotes"])  # grab all votes
    for user_id in mvotes:
        vote = mvotes[user_id]
        votes = list(map(add, votes, vote))

    indices = [i for i, x in enumerate(votes) if x == max(votes)]
    days = list(map(lambda x:indexToDay[x], indices))
    yield from bot.coro_send_message(event.conv, _("Pizzaday could be on {}").format(days))
    yield from bot.coro_send_message(event.conv, _("I recommend to eat pizza on {}").format(random.choice(days)))

def dumpvotes(bot, event, *args):
    initMemory(bot)

    mvotes = bot.memory.get_by_path(["pizzavotes"])  # grab all votes
    for user_id in mvotes:
        vote = mvotes[user_id]
        yield from bot.coro_send_message(event.conv, _("Vote for " + user_id + ": {}").format(vote))

def initMemory(bot):
    if not bot.memory.exists(["pizzavotes"]):
        bot.memory.set_by_path(["pizzavotes"], {})
        bot.memory.save()

def resetvotes(bot, event, *args):
    initMemory(bot)

    counter = 0
    bot.memory.set_by_path(["pizzavotes"], {})
    bot.memory.save()
    yield from bot.coro_send_message(event.conv, _("Deleted {} vote(s)").format(counter))

def vote(bot, event, *args):
    initMemory(bot)

    if not args:
        yield from bot.coro_send_message(event.conv, _("Usage: /bot vote <i>Mon-Wed,Fri</i>\n/bot vote {}"))
        return

    if len(args) == 1 and args[0] in noVote:
        bot.memory.set_by_path(["pizzavotes", event.user.id_.chat_id], [0] * 5)
        bot.memory.save()
        yield from bot.coro_send_message(event.conv, _("No pizza for you, sucker."))
        return

    try:
        vote = voteForPizza(bot, ",".join(args))
        bot.memory.set_by_path(["pizzavotes", event.user.id_.chat_id], vote)
        bot.memory.save()
        yield from bot.coro_send_message(event.conv, _("Thank you for voting ({})").format(vote))
    except Exception as ex:
        yield from bot.coro_send_message(event.conv, _("Error: Do you even syntax?! " + ex))

def voteForPizza(bot, inp):
    groups = inp.lower().split(",")
    days = map(lambda x:x.split("-"), groups)
    ranges = map(lambda x:map(lambda y:dayToIndex[y[:2]], x), days)
    vote = [0]*5
    for ri in ranges:
        r = list(ri)
        if len(r) == 1 and r[0] in validDays:
            vote[r[0]] += 1
        elif len(r) == 2 and r[0] in validDays and r[1] in validDays and r[0] < r[1]:
            for d in range(r[0], r[1] + 1):
                vote[d] += 1
        else:
            raise ValueError("You suck.")
    #Clean
    vote = list(map(lambda x:min(x, 1), vote))
    return vote