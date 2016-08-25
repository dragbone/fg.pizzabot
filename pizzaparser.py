""" Doesn't actually parse pizzas """
import re
import random
import datetime
from operator import add

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