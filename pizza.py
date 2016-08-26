import plugins
import re
import random
import datetime
from operator import add


def _initialise(bot):
    plugins.register_user_command(["vote", "pizza"])
    plugins.register_admin_command(["resetvotes", "dumpvotes"])


indexToDay = {0: "Monday",
              1: "Tuesday",
              2: "Wednesday",
              3: "Thursday",
              4: "Friday"}


def pizza(bot, event, *args):
    (votes, canAttend) = countVotes(getVotes(bot))

    indices = [i for i, x in enumerate(votes) if x == max(votes)]
    days = list(map(lambda x: indexToDay[x], indices))

    recommendedDay = choosePizzaDay(indices)
    message = "Pizzaday could be on " + days + "\n"
    message += "I recommend to eat pizza on " + indexToDay[recommendedDay] + "\n"
    message += ", ".join(canAttend[recommendedDay]) + " will be attending"
    yield from bot.coro_send_message(event.conv, message)


def countVotes(mvotes):
    votes = [0] * 5
    canAttend = [[] for i in range(5)]
    for user_id in mvotes:
        vote = mvotes[user_id]
        votes = list(map(add, votes, vote["vote"]))
        for i, d in enumerate(vote["vote"]):
            if d == 1:
                canAttend[i].append(vote["name"])
            elif d == 0.5:
                canAttend[i].append("(" + vote["name"] + ")")
    return (votes, canAttend)


def dumpvotes(bot, event, *args):
    mvotes = getVotes(bot)
    for user_id in mvotes:
        vote = mvotes[user_id]
        yield from bot.coro_send_message(event.conv, _("Vote for " + vote["name"] + ": {}").format(vote["vote"]))


def resetvotes(bot, event, *args):
    clearMemory(bot)
    yield from bot.coro_send_message(event.conv, _("Deleted all votes"))


def vote(bot, event, *args):
    if not args:
        yield from bot.coro_send_message(event.conv, _("Usage: /bot vote <i>Mon-Wed,(Fri)</i>\n/bot vote {}"))
        return

    try:
        vote = parsePizzaVote(args)
        storeVote(bot, event.user, vote)
        yield from bot.coro_send_message(event.conv, _("Thank you for voting ({})").format(vote))
    except Exception as ex:
        yield from bot.coro_send_message(event.conv, _("Error: Do you even syntax?! " + ex))


# MEMORY
# Stores votes and stuff (no pizzas, sorry!)
MEM_NAME = "pizzavotes"


def initMemory(bot):
    if not bot.memory.exists([MEM_NAME]):
        bot.memory.set_by_path([MEM_NAME], {})
        bot.memory.save()


def clearMemory(bot):
    initMemory(bot)
    bot.memory.set_by_path([MEM_NAME], {})
    bot.memory.save()


def storeVote(bot, user, vote):
    initMemory(bot)
    bot.memory.set_by_path([MEM_NAME, user.id_.chat_id], {"name": user.full_name, "vote": vote})
    bot.memory.save()


def getVotes(bot):
    initMemory(bot)
    return bot.memory.get_by_path([MEM_NAME])


# PIZZAPARSER
# Doesn't actually parse pizzas
noVote = ["none", "null", "{}", "()", "nada", "never", ":-(", ":'-("]
dayToIndex = {"mo": 0,
              "di": 1, "tu": 1,
              "mi": 2, "we": 2,
              "do": 3, "th": 3,
              "fr": 4}


class VoteRange:
    def __init__(self, text):
        match = re.match("\((.+)\)", text)
        if match is None:
            value = 1.0
            inner = text
        else:
            value = 0.5
            inner = match.group(1)

        days = list(map(lambda x: dayToIndex[x[:2]], inner.split("-")))
        self.vote = [0] * 5
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
    voteRanges = map(lambda x: VoteRange(x), groups)
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
