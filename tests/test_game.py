"""Pruebas de integración de Pygame con controlador SDL virtual."""

import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import unittest
import pygame

from main import Game
from mathinvaders.sprites import Laser


class GameSmokeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.game = Game()

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def setUp(self):
        self.game.new_game()

    def test_images_game_loop_and_screen_render(self):
        self.assertEqual(len(self.game.stars), 5)
        for _ in range(5):
            self.game.update(1 / 60)
        self.game.draw_game()
        self.game.draw_menu()
        self.game.draw_game_over()

    def test_correct_hit_starts_new_round_with_five_stars(self):
        original = self.game.engine.equation
        target = next(
            star for star in self.game.stars
            if star.number == original.answer
        )
        self.game.lasers.add(Laser(
            self.game.images["laser"], target.rect.centerx,
            target.rect.bottom + 1
        ))
        self.game.resolve_collisions()
        self.assertEqual(self.game.engine.correct_answers, 1)
        self.assertEqual(len(self.game.stars), 5)
        self.assertNotEqual(self.game.engine.equation, original)

    def test_wrong_hit_does_not_advance(self):
        original = self.game.engine.equation
        target = next(
            star for star in self.game.stars
            if star.number != original.answer
        )
        self.game.lasers.add(Laser(
            self.game.images["laser"], target.rect.centerx,
            target.rect.bottom + 1
        ))
        self.game.resolve_collisions()
        self.assertEqual(self.game.engine.equation, original)
        self.assertEqual(self.game.engine.correct_answers, 0)
        self.assertEqual(len(self.game.stars), 5)
        self.assertLess(self.game.engine.score, 0)


if __name__ == "__main__":
    unittest.main()
