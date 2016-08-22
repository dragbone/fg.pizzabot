import plugins
import random

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
    indices = [i for i, x in enumerate(bot.votes) if x == max(bot.votes)]
    days = map(lambda x:indexToDay[x], indices)
    yield from bot.coro_send_message(event.conv, _("Pizzaday could be on {}").format(days))
    yield from bot.coro_send_message(event.conv, _("I recommend to eat pizza on {}").format(random.choice(days)))

def resetvote(bot, event, *args):
    bot.votes = [0]*5

def vote(bot, event, *args):
    """
    Vote for the next pizza day

    /bot vote <i>Mon-Wed,Fri</i>
    """

    if not args:
        yield from bot.coro_send_message(event.conv, _("Usage: /bot vote <i>Mon-Wed,Fri</i>"))
        return

    try:
        voteForPizza(bot, ",".join(args))
        yield from bot.coro_send_message(event.conv, _("Thank you for voting."))
    except ValueError:
        yield from bot.coro_send_message(event.conv, _("Error: Do you even syntax."))


def voteForPizza(bot, input):
    groups = input.lower().split(",")
    days = map(lambda x:x.split("-"),groups)
    ranges = map(lambda x:map(lambda y:dayToIndex[y[:2]],x),days)

    for r in ranges:
        if len(r) == 1:
            bot.votes[r[0]] += 1
        elif len(r) == 2:
            for d in range(r[0],r[1]+1):
                bot.votes[d] += 1
        else:
            raise ValueError("urgh")