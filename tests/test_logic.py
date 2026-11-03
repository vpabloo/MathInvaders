"""Pruebas del motor educativo; no requieren Pygame."""

import random
import unittest

from mathinvaders.logic import Equation, MathEngine


class EquationTests(unittest.TestCase):
    def test_arithmetic(self):
        self.assertEqual(Equation(5, 3, "+").answer, 8)
        self.assertEqual(Equation(5, 3, "-").answer, 2)
        with self.assertRaises(ValueError):
            _ = Equation(5, 3, "*").answer


class MathEngineTests(unittest.TestCase):
    def setUp(self):
        self.engine = MathEngine(rng=random.Random(42))

    def test_always_one_correct_option_and_five_unique_choices(self):
        for _ in range(100):
            choices = self.engine.choices
            self.assertEqual(len(choices), 5)
            self.assertEqual(len(set(choices)), 5)
            self.assertEqual(choices.count(self.engine.equation.answer), 1)
            self.engine.next_round()

    def test_wrong_answer_penalizes_and_keeps_equation(self):
        equation = self.engine.equation
        wrong = next(x for x in self.engine.choices if x != equation.answer)
        self.assertFalse(self.engine.submit(wrong))
        self.assertEqual(self.engine.equation, equation)
        self.assertEqual(self.engine.score, -max(1, wrong // 2))
        self.assertEqual(self.engine.wrong_answers, 1)

    def test_wrong_one_penalizes_one_point(self):
        self.engine.score = 0
        self.engine.equation = Equation(2, 2, "+")
        self.assertFalse(self.engine.submit(1))
        self.assertEqual(self.engine.score, -1)

    def test_correct_answer_ends_round_and_increases_score(self):
        answer = self.engine.equation.answer
        self.assertTrue(self.engine.submit(answer))
        self.assertEqual(self.engine.score, answer)
        self.assertEqual(self.engine.correct_answers, 1)
        with self.assertRaises(RuntimeError):
            self.engine.submit(answer)
        self.engine.next_round()
        self.assertEqual(self.engine.correct_answers, 1)

    def test_level_depends_on_correct_answers_not_destroyed_stars(self):
        for _ in range(5):
            self.engine.submit(self.engine.equation.answer)
            self.engine.next_round()
        self.assertEqual(self.engine.level, 2)
        for _ in range(5):
            self.engine.submit(self.engine.equation.answer)
            self.engine.next_round()
        self.assertEqual(self.engine.level, 3)

    def test_subtraction_unlocked_from_level_three(self):
        self.engine.level = 3
        seen = set()
        for _ in range(100):
            self.engine.next_round()
            seen.add(self.engine.equation.operator)
            self.assertGreaterEqual(self.engine.equation.answer, 0)
        self.assertEqual(seen, {"+", "-"})

    def test_lives_and_reset(self):
        self.assertFalse(self.engine.lose_life())
        self.assertFalse(self.engine.lose_life())
        self.assertTrue(self.engine.lose_life())
        self.assertTrue(self.engine.lose_life())
        self.assertEqual(self.engine.lives, 0)
        self.engine.reset()
        self.assertEqual(self.engine.lives, 3)
        self.assertEqual(self.engine.level, 1)
        self.assertEqual(self.engine.score, 0)

    def test_invalid_config(self):
        with self.assertRaises(ValueError):
            MathEngine(questions_per_level=0)
        with self.assertRaises(ValueError):
            MathEngine(initial_lives=0)


if __name__ == "__main__":
    unittest.main()
