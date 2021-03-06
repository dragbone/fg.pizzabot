import unittest
import pizza


class ParserTests(unittest.TestCase):
    def assertListContentEqual(self, list1, list2):
        self.assertEqual(len(list1), len(list2))
        self.assertEqual(sorted(list1), sorted(list2))

    def test_non_vote(self):
        self.assertEqual([0, 0, 0, 0, 0], pizza.parsePizzaVote(["none"]))

    def test_range(self):
        self.assertEqual([1, 1, 1, 1, 1], pizza.parsePizzaVote(["Mon-Fri"]))
        self.assertEqual([1, 1, 0, 0, 0], pizza.parsePizzaVote(["Mon-Tue"]))
        self.assertEqual([0, 0, 1, 1, 1], pizza.parsePizzaVote(["Wed-Fri"]))

    def test_single(self):
        self.assertEqual([1, 0, 0, 0, 0], pizza.parsePizzaVote(["Mon"]))
        self.assertEqual([1, 1, 0, 0, 0], pizza.parsePizzaVote(["Mon", "Tue"]))
        self.assertEqual([1, 0, 0, 0, 1], pizza.parsePizzaVote(["Mon", "Fri"]))

    def test_ifneeded(self):
        self.assertEqual([0.5, 0, 0, 0, 0], pizza.parsePizzaVote(["(Mon)"]))
        self.assertEqual([0.5, 0.5, 0, 0, 0], pizza.parsePizzaVote(["(Mon)", "(Tue)"]))
        self.assertEqual([0.5, 1, 0, 0, 0], pizza.parsePizzaVote(["(Mon)", "Tue"]))
        self.assertEqual([0.5, 0.5, 0.5, 0, 0], pizza.parsePizzaVote(["(Mon-Wed)"]))

    def test_cheater(self):
        self.assertEqual([1, 0, 0, 0, 0], pizza.parsePizzaVote(["Mon", "Mon"]))
        self.assertEqual([1, 0, 0, 0, 0], pizza.parsePizzaVote(["(Mon)", "(Mon)"]))
        self.assertEqual([1, 1, 0, 0, 0], pizza.parsePizzaVote(["(Mon)", "Mon-Tue"]))
        self.assertEqual([1, 1, 0, 0, 0], pizza.parsePizzaVote(["Mon", "Mon-Tue"]))
        self.assertEqual([1, 0.5, 0, 0, 0], pizza.parsePizzaVote(["Mon", "(Mon-Tue)"]))

    def test_parse_sep(self):
        self.assertEqual([1, 1, 0, 0, 0], pizza.parsePizzaVote(["Mon,", "Tue"]))
        self.assertEqual([1, 1, 0, 0, 0], pizza.parsePizzaVote(["Mon,Tue"]))
        self.assertEqual([1, 1, 0, 0, 0], pizza.parsePizzaVote(["Mon", "Tue"]))

    def test_parse_lan(self):
        self.assertEqual([1, 1, 1, 1, 1], pizza.parsePizzaVote(["mon", "tue", "wed", "thu", "fri"]))
        self.assertEqual([1, 1, 1, 1, 1], pizza.parsePizzaVote(["Mon", "Tue", "Wed", "Thu", "Fri"]))
        self.assertEqual([1, 1, 1, 1, 1], pizza.parsePizzaVote(["mo", "di", "mi", "do", "fr"]))
        self.assertEqual([1, 1, 1, 1, 1], pizza.parsePizzaVote(["Mo", "Di", "Mi", "Do", "Fr"]))

    def test_stable_random(self):
        day = pizza.choosePizzaDay(range(0, 5))

        for i in range(0, 5):
            # Remove day i from options, selected day must not change except if i == selected_day
            days = list(range(0, 5))
            days.remove(i)
            nDay = pizza.choosePizzaDay(days)
            if i != day:
                self.assertEqual(day, nDay)
            else:
                self.assertNotEqual(day, nDay)

    def test_parse_fail(self):
        self.assertRaises(Exception, pizza.parsePizzaVote, ["xu"])
        self.assertRaises(Exception, pizza.parsePizzaVote, ["mo-tu-fr"])
        self.assertRaises(Exception, pizza.parsePizzaVote, ["123"])
        self.assertRaises(Exception, pizza.parsePizzaVote, ["[0,2]"])
        self.assertRaises(Exception, pizza.parsePizzaVote, ["mo", "null"])
        self.assertRaises(Exception, pizza.parsePizzaVote, ["(mo)", "((wed))"])

    def test_count_votes(self):
        (votes, canAttend) = pizza.countVotes({
            "123": {
                "name": "person1",
                "vote": [0, 0, 1, 1, 1]
            },
            "456": {
                "name": "person2",
                "vote": [1, 0, 0.5, 0, 0]
            }
        })
        self.assertEqual([1, 0, 1.5, 1, 1], votes)
        self.assertListContentEqual(["person2"], canAttend[0])
        self.assertListContentEqual([], canAttend[1])
        self.assertListContentEqual(["person1", "(person2)"], canAttend[2])
        self.assertListContentEqual(["person1"], canAttend[3])
        self.assertListContentEqual(["person1"], canAttend[4])

class IssueTests(unittest.TestCase):
    def test_issue1_empty_vote(self):
        self.assertEqual([0, 0, 0, 0, 0], pizza.parsePizzaVote(["null"]))
        self.assertEqual([0, 0, 0, 0, 0], pizza.parsePizzaVote(["{}"]))

    def test_issue2_ifneedbe(self):
        self.assertEqual([1, 0.5, 1, 0.5, 0.5], pizza.parsePizzaVote(["mo,", "(di),", "mi,", "(do-fr)"]))

    def test_issue3_deterministic_random(self):
        firstDay = pizza.choosePizzaDay(range(0, 5))
        for i in range(0, 100):
            self.assertEqual(firstDay, pizza.choosePizzaDay(range(0, 5)))


if __name__ == '__main__':
    unittest.main()
