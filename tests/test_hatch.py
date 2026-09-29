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


class EarlyClaimTest(unittest.TestCase):
    def test_claim_before_duration_raises(self):
        egg = Egg("e", 0, 3600)
        with self.assertRaises(HatchError):
            claim(egg, 100)
        self.assertFalse(egg.claimed)

    def test_claim_at_exact_duration_ok(self):
        egg = Egg("e", 0, 3600)
        self.assertTrue(claim(egg, 3600))
        self.assertTrue(egg.claimed)


class RepeatClaimTest(unittest.TestCase):
    def test_second_claim_raises(self):
        egg = Egg("e", 0, 100)
        self.assertTrue(claim(egg, 500))
        with self.assertRaises(HatchError):
            claim(egg, 600)

    def test_claimed_flag_stays_true(self):
        egg = Egg("e", 0, 100)
        claim(egg, 500)
        for now in (600, 700, 800):
            with self.assertRaises(HatchError):
                claim(egg, now)
            self.assertTrue(egg.claimed)


class BoostTest(unittest.TestCase):
    def test_second_boost_raises(self):
        egg = Egg("e", 0, 100)
        boost(egg, 30)
        with self.assertRaises(HatchError):
            boost(egg, 30)
        self.assertEqual(egg.start, -30)

    def test_boost_shortens_required_time(self):
        egg = Egg("e", 0, 100)
        boost(egg, 40)
        self.assertEqual(progress(egg, 60), 1.0)
        self.assertTrue(claim(egg, 60))

    def test_boost_error_carries_egg_id(self):
        egg = Egg("e42", 0, 100)
        boost(egg, 10)
        with self.assertRaises(HatchError) as ctx:
            boost(egg, 10)
        self.assertEqual(ctx.exception.egg_id, "e42")


class InvariantTest(unittest.TestCase):
    def test_progress_within_bounds(self):
        egg = Egg("e", 10, 100)
        boost(egg, 50)
        for now in (-100, 0, 10, 60, 110, 10 ** 6):
            value = progress(egg, now)
            self.assertGreaterEqual(value, 0.0)
            self.assertLessEqual(value, 1.0)

    def test_same_ops_same_result(self):
        def run():
            egg = Egg("e", 0, 100)
            boost(egg, 25)
            first = progress(egg, 50)
            try:
                claim(egg, 50)
            except HatchError:
                pass
            ok = claim(egg, 75)
            return first, ok, egg.claimed

        self.assertEqual(run(), run())


class ReferenceComparisonTest(unittest.TestCase):
    """随机 200 组「加速 + 等待 + 领取」时间线，与参考实现逐步比对。"""

    def test_matches_reference(self):
        import random

        rng = random.Random(20240930)
        for _ in range(200):
            duration = rng.randint(1, 10000)
            egg = Egg("e", 0, duration)
            ref = {"start": 0, "duration": duration, "boost_used": False, "claimed": False}
            now = 0
            for _ in range(rng.randint(1, 20)):
                op = rng.choice(["boost", "wait", "claim"])
                if op == "boost":
                    amount = rng.randint(1, 500)
                    impl_error = False
                    try:
                        boost(egg, amount)
                    except HatchError:
                        impl_error = True
                    ref_error = ref["boost_used"]
                    if not ref_error:
                        ref["boost_used"] = True
                        ref["start"] -= amount
                    self.assertEqual(impl_error, ref_error)
                elif op == "wait":
                    now += rng.randint(0, 2000)
                else:
                    impl_error = False
                    try:
                        claim(egg, now)
                    except HatchError:
                        impl_error = True
                    ref_error = ref["claimed"] or now - ref["start"] < ref["duration"]
                    if not ref_error:
                        ref["claimed"] = True
                    self.assertEqual(impl_error, ref_error)
                elapsed = max(0, now - ref["start"])
                expected = min(1.0, elapsed / ref["duration"])
                self.assertEqual(progress(egg, now), expected)
                self.assertEqual(egg.claimed, ref["claimed"])


class ScaleTest(unittest.TestCase):
    def test_100k_eggs_100k_queries_under_1s(self):
        import time

        eggs = [Egg(i, 0, 3600) for i in range(100000)]
        start = time.perf_counter()
        total = 0.0
        for egg in eggs:
            total += progress(egg, 100)
        elapsed = time.perf_counter() - start
        self.assertGreater(total, 0.0)
        self.assertLess(elapsed, 1.0)
