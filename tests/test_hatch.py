import unittest

from pethatch.hatch import Egg, HatchError, boost, claim, progress


class ProgressTest(unittest.TestCase):
    def test_zero_at_start(self):
        self.assertEqual(progress(Egg("e", 0, 100), 0), 0.0)

    def test_half_way(self):
        self.assertEqual(progress(Egg("e", 0, 100), 50), 0.5)

    def test_capped_at_one(self):
        self.assertEqual(progress(Egg("e", 0, 100), 1000), 1.0)

    def test_error_type(self):
        self.assertTrue(issubclass(HatchError, ValueError))


class ClaimTest(unittest.TestCase):
    def test_repeat_sets_flag(self):
        egg = Egg("e", 0, 100)
        claim(egg, 500)
        self.assertTrue(egg.claimed)

    def test_boost_moves_start(self):
        egg = Egg("e", 0, 100)
        boost(egg, 30)
        self.assertEqual(egg.start, -30)


if __name__ == "__main__":
    unittest.main()
