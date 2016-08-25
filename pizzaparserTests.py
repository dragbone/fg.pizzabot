import unittest
import pizza

class ParserTests(unittest.TestCase):
    def test_non_vote(self):
        self.assertEqual([0, 0, 0, 0, 0], pizza.parsePizzaVote(["none"]))

    def test_range(self):
        self.assertEqual([1, 1, 1, 1, 1], pizza.parsePizzaVote(["Mon-Fri"]))
        self.assertEqual([1, 1, 0, 0, 0], pizza.parsePizzaVote(["Mon-Tue"]))
        self.assertEqual([0, 0, 1, 1, 1], pizza.parsePizzaVote(["Wed-Fri"]))

    def test_single(self):
        self.assertEqual([1, 0, 0, 0, 0], pizza.parsePizzaVote(["Mon"]))
        self.assertEqual([1, 1, 0, 0, 0], pizza.parsePizzaVote(["Mon","Tue"]))
        self.assertEqual([1, 0, 0, 0, 1], pizza.parsePizzaVote(["Mon","Fri"]))

    def test_ifneeded(self):
        self.assertEqual([0.5, 0, 0, 0, 0], pizza.parsePizzaVote(["(Mon)"]))
        self.assertEqual([0.5, 0.5, 0, 0, 0], pizza.parsePizzaVote(["(Mon)","(Tue)"]))
        self.assertEqual([0.5, 1, 0, 0, 0], pizza.parsePizzaVote(["(Mon)", "Tue"]))
        self.assertEqual([0.5, 0.5, 0.5, 0, 0], pizza.parsePizzaVote(["(Mon-Wed)"]))

    def test_cheater(self):
        self.assertEqual([1, 0, 0, 0, 0], pizza.parsePizzaVote(["Mon","Mon"]))
        self.assertEqual([1, 0, 0, 0, 0], pizza.parsePizzaVote(["(Mon)","(Mon)"]))
        self.assertEqual([1, 1, 0, 0, 0], pizza.parsePizzaVote(["(Mon)","Mon-Tue"]))
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
        day = pizza.choosePizzaDay(range(0,5))

        for i in range(0,5):
            # Remove day i from options, selected day must no change except if i == selected_day
            days = list(range(0,5))
            days.remove(i)
            nDay = pizza.choosePizzaDay(days)
            if i != day:
                self.assertEqual(day, nDay)
            else:
                self.assertNotEqual(day, nDay)

class IssueTests(unittest.TestCase):
    def test_issue1_empty_vote(self):
        self.assertEqual([0, 0, 0, 0, 0], pizza.parsePizzaVote(["null"]))
        self.assertEqual([0, 0, 0, 0, 0], pizza.parsePizzaVote(["{}"]))

    def test_issue2_ifneedbe(self):
        self.assertEqual([1, 0.5, 1, 0.5, 0.5], pizza.parsePizzaVote(["mo,", "(di),", "mi,", "(do-fr)"]))

    def test_issue3_deterministic_random(self):
        firstDay = pizza.choosePizzaDay(range(0, 5))
        for i in range(0,100):
            self.assertEqual(firstDay, pizza.choosePizzaDay(range(0, 5)))

if __name__ == '__main__':
    unittest.main()
