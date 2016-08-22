import plugins
import random
from operator import add

def _initialise(bot):
    plugins.register_user_command(["vote","pizza"])
    plugins.register_admin_command(["resetvote"])


indexToDay = {0:"Monday",
              1:"Tuesday",
              2:"Wednesday",
              3:"Thursday",
              4:"Friday"}

dayToIndex = {"mo":0,
              "di":1, "tu":1,
              "mi":2, "we":2,
              "do":3, "th":3,
              "fr":4
              }

def pizza(bot, event, *args):
    initMemory(bot)

    votes = [0] * 5
    mvotes = bot.memory.get_by_path(["pizzavotes"])  # grab all votes
    for user_id in mvotes:
        vote = votes[user_id]
        votes = map(add, votes, vote)

    indices = [i for i, x in enumerate(votes) if x == max(votes)]
    days = map(lambda x:indexToDay[x], indices)
    yield from bot.coro_send_message(event.conv, _("Pizzaday could be on {}").format(days))
    yield from bot.coro_send_message(event.conv, _("I recommend to eat pizza on {}").format(random.choice(days)))

def initMemory(bot):
    if not bot.memory.exists(["pizzavotes"]):
        bot.memory.set_by_path(["pizzavotes"], {})
        bot.memory.save()

def resetvote(bot, event, *args):
    initMemory(bot)

    counter = 0
    votes = bot.memory.get_by_path(["pizzavotes"])  # grab all votes
    for user_id in votes:
        bot.memory.pop_by_path(["pizzavotes", user_id])
        counter += 1
    bot.memory.save()
    yield from bot.coro_send_message(event.conv, _("Deleted {} vote(s)").format(counter))

def vote(bot, event, *args):
    initMemory(bot)

    if not args:
        yield from bot.coro_send_message(event.conv, _("Usage: /bot vote <i>Mon-Wed,Fri</i>"))
        return

    try:
        vote = voteForPizza(bot, ",".join(args))
        bot.memory.set_by_path(["pizzavotes", event.user.id_.chat_id], vote)
        bot.memory.save()
        #bot.user_memory_set(event.user.id_.chat_id, 'pizzavote', vote)
        yield from bot.coro_send_message(event.conv, _("Thank you for voting."))
    except ValueError:
        yield from bot.coro_send_message(event.conv, _("Error: Do you even syntax."))


def voteForPizza(bot, inp):
    groups = inp.lower().split(",")
    days = map(lambda x:x.split("-"), groups)
    ranges = map(lambda x:map(lambda y:dayToIndex[y[:2]], x), days)
    vote = [0]*5
    for ri in ranges:
        r = list(ri)
        if len(r) == 1:
            vote[r[0]] += 1
        elif len(r) == 2:
            for d in range(r[0], r[1] + 1):
                vote[d] += 1
        else:
            raise ValueError("urgh")
    #Clean
    vote = map(lambda x:min(x, 1), vote)
    return vote