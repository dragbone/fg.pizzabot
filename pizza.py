import plugins
import re
import random
import datetime
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

    recommendedDay = indexToDay[choosePizzaDay(indices)]
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

    bot.memory.set_by_path([MEM_NAME], {})
    bot.memory.save()
    yield from bot.coro_send_message(event.conv, _("Deleted all votes"))

def vote(bot, event, *args):
    initMemory(bot)

    if not args:
        yield from bot.coro_send_message(event.conv, _("Usage: /bot vote <i>Mon-Wed,(Fri)</i>\n/bot vote {}"))
        return

    try:
        vote = parsePizzaVote(args)
        bot.memory.set_by_path([MEM_NAME, event.user.id_.chat_id], vote)
        bot.memory.save()
        yield from bot.coro_send_message(event.conv, _("Thank you for voting ({})").format(vote))
    except Exception as ex:
        yield from bot.coro_send_message(event.conv, _("Error: Do you even syntax?! " + ex))

# PIZZAPARSER
# Doesn't actually parse pizzas

noVote = ["none", "null", "{}", "()", "nada", "never", ":-(", ":'-("]

dayToIndex = {"mo":0,
              "di":1, "tu":1,
              "mi":2, "we":2,
              "do":3, "th":3,
              "fr":4}

class VoteRange:
    def __init__(self, text):
        match = re.match("\((.+)\)", text)
        if match is None:
            value = 1.0
            inner = text
        else:
            value = 0.5
            inner = match.group(1)

        days = list(map(lambda x : dayToIndex[x[:2]], inner.split("-")))
        self.vote = [0]*5
        if len(days) == 1:
            self.vote[days[0]] += value
        elif len(days) == 2 and days[0] < days[1]:
            for day in range(days[0], days[1] + 1):
                self.vote[day] += value
        else:
            raise ValueError("You suck.")

    def applyVote(self, votes):
        return list(map(add, votes, self.vote))

def parsePizzaVote(args):
    vote = [0] * 5

    if len(args) == 1 and args[0].lower() in noVote:
        return vote

    groups = map(lambda y: y.lower(), filter(lambda x: len(x) > 0, ",".join(args).split(",")))
    voteRanges = map(lambda x : VoteRange(x), groups)
    for vr in voteRanges:
        vote = vr.applyVote(vote)

    # Clean
    vote = list(map(lambda x: min(x, 1.0), vote))
    return vote

def choosePizzaDay(days):
    # Recommend a random day - recommended day does not change with additional votes,
    #   as long as it is one of the most often voted ones
    random.seed(datetime.datetime.now().isocalendar()[1])
    dayPriorities = list(range(0, 5))
    random.shuffle(dayPriorities)
    return max(days, key=lambda x: dayPriorities[x])
