"""Interfaz de MathInvaders. Las reglas viven en mathinvaders.logic."""

from pathlib import Path
import random

import pygame

from mathinvaders.logic import MathEngine
from mathinvaders.sprites import Laser, Player, Star


ROOT = Path(__file__).resolve().parent
WIDTH, HEIGHT = 1080, 686
FPS = 60
STARS_PER_ROUND = 5
WHITE = (250, 250, 255)


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Math Invaders")
        self.clock = pygame.time.Clock()
        self.rng = random.Random()
        self.images = {
            "background": self.load_image("wallpaper.jpg", (WIDTH, HEIGHT), alpha=False),
            "player": self.load_image("rocket.png", (72, 72)),
            "laser": self.load_image("laser.png", (16, 32)),
            "star": self.load_image("star.png", (64, 64)),
            "heart": self.load_image("heart.png", (20, 20)),
        }
        font_path = ROOT / "VT323-Regular.ttf"
        self.font = pygame.font.Font(str(font_path), 36)
        self.big_font = pygame.font.Font(str(font_path), 76)
        self.number_font = pygame.font.Font(str(font_path), 44)
        self.overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self.overlay.fill((4, 7, 22, 190))
        self.hud_panel = pygame.Surface((530, 112), pygame.SRCALPHA)
        self.hud_panel.fill((0, 0, 0, 145))
        self.laser_sound = None
        if pygame.mixer.get_init():
            try:
                self.laser_sound = pygame.mixer.Sound(str(ROOT / "sounds" / "lasser.wav"))
                self.laser_sound.set_volume(0.35)
            except (pygame.error, OSError):
                pass  # El juego funciona aunque no haya audio.
        self.restart_button = pygame.Rect(WIDTH // 2 - 150, HEIGHT // 2 + 140, 300, 60)
        self.new_game()
        self.state = "menu"

    @staticmethod
    def load_image(filename, size, alpha=True):
        source = ROOT / "images" / filename
        image = pygame.image.load(str(source))
        image = image.convert_alpha() if alpha else image.convert()
        return pygame.transform.smoothscale(image, size)

    def new_game(self):
        self.engine = MathEngine(rng=self.rng)
        self.player = Player(self.images["player"], WIDTH, HEIGHT)
        self.stars = pygame.sprite.Group()
        self.lasers = pygame.sprite.Group()
        self.messages = []
        self.invulnerability = 0.0
        self.shoot_cooldown = 0.0
        self.spawn_wave()
        self.state = "playing"

    def spawn_star(self, number, slot, fast=False):
        star = Star(
            self.images["star"], self.number_font, number, slot,
            STARS_PER_ROUND, WIDTH, HEIGHT, self.engine.level, fast, self.rng
        )
        self.stars.add(star)

    def spawn_wave(self):
        self.stars.empty()
        self.lasers.empty()
        fast_count = min(STARS_PER_ROUND, self.engine.level // 5)
        fast_slots = set(self.rng.sample(range(STARS_PER_ROUND), fast_count))
        for slot, number in enumerate(self.engine.choices):
            self.spawn_star(number, slot, fast=slot in fast_slots)

    def add_message(self, message, x, y, color):
        self.messages.append({
            "text": message, "x": x, "y": float(y),
            "color": color, "remaining": 1.1,
        })

    def shoot(self):
        if self.shoot_cooldown > 0:
            return
        self.lasers.add(Laser(
            self.images["laser"], self.player.rect.centerx, self.player.rect.top
        ))
        self.shoot_cooldown = 0.18
        if self.laser_sound:
            self.laser_sound.play()

    def update(self, dt):
        self.shoot_cooldown = max(0, self.shoot_cooldown - dt)
        self.invulnerability = max(0, self.invulnerability - dt)
        self.player.update(dt)
        self.stars.update(dt)
        self.lasers.update(dt)
        self.update_messages(dt)
        self.resolve_collisions()

    def update_messages(self, dt):
        for message in self.messages:
            message["remaining"] -= dt
            message["y"] -= 42 * dt
        self.messages = [m for m in self.messages if m["remaining"] > 0]

    def resolve_collisions(self):
        # Reponer cualquier estrella que choque con la nave; no cambia de valor.
        impacts = pygame.sprite.spritecollide(self.player, self.stars, dokill=True)
        for star in impacts:
            self.spawn_star(star.number, star.slot, star.fast)
        if impacts and self.invulnerability == 0:
            ended = self.engine.lose_life()
            self.invulnerability = 1.2
            if ended:
                self.state = "over"
                return

        # Una respuesta correcta termina la pregunta, no exige destruir distractores.
        hits = pygame.sprite.groupcollide(self.stars, self.lasers, True, True)
        for star in hits:
            correct = self.engine.submit(star.number)
            if correct:
                self.add_message("¡CORRECTO!", star.rect.centerx, star.rect.centery,
                                 (90, 255, 130))
                self.engine.next_round()
                self.spawn_wave()
                return
            self.add_message("INCORRECTO", star.rect.centerx, star.rect.centery,
                             (255, 95, 95))
            self.spawn_star(star.number, star.slot, star.fast)

    def draw_text(self, text, x, y, *, font=None, color=WHITE, centered=False):
        surface = (font or self.font).render(text, True, color)
        if centered:
            x -= surface.get_width() // 2
        self.screen.blit(surface, (x, y))
        return surface

    def draw_game(self):
        self.screen.blit(self.images["background"], (0, 0))
        self.stars.draw(self.screen)
        for star in self.stars:
            if star.fast and pygame.time.get_ticks() // 180 % 2 == 0:
                pygame.draw.rect(self.screen, (255, 90, 90),
                                 star.rect.inflate(6, 6), width=3)
        self.lasers.draw(self.screen)
        if self.invulnerability == 0 or pygame.time.get_ticks() // 120 % 2 == 0:
            self.screen.blit(self.player.image, self.player.rect)
        self.draw_hud()
        for message in self.messages:
            surface = self.font.render(message["text"], True, message["color"])
            surface.set_alpha(int(255 * min(1, message["remaining"])))
            self.screen.blit(surface, (
                message["x"] - surface.get_width() // 2, int(message["y"])
            ))

    def draw_hud(self):
        self.screen.blit(self.hud_panel, (10, 10))
        self.draw_text(self.engine.equation.label, 25, 18, font=self.big_font)
        level_label = self.font.render(f"Nivel: {self.engine.level}", True, WHITE)
        self.screen.blit(level_label, (WIDTH - level_label.get_width() - 18, 10))
        # Alinear correctamente el marcador sin depender de su número de cifras.
        score_label = self.font.render(f"Puntos: {self.engine.score}", True, WHITE)
        self.screen.blit(score_label, (WIDTH - score_label.get_width() - 18, 49))
        for i in range(self.engine.lives):
            self.screen.blit(self.images["heart"], (WIDTH - 34 - i * 27, 91))

    def draw_menu(self):
        self.draw_game()
        self.screen.blit(self.overlay, (0, 0))
        self.draw_text("MATH INVADERS", WIDTH // 2, 170,
                       font=self.big_font, centered=True)
        self.draw_text("Resuelve la operación y dispara al número correcto",
                       WIDTH // 2, 290, centered=True)
        self.draw_text("W A S D: mover    ESPACIO: disparar",
                       WIDTH // 2, 346, centered=True)
        self.draw_text("Haz clic o presiona ENTER para jugar",
                       WIDTH // 2, 425, centered=True, color=(255, 215, 95))

    def draw_game_over(self):
        self.draw_game()
        self.screen.blit(self.overlay, (0, 0))
        self.draw_text("GAME OVER", WIDTH // 2, 165,
                       font=self.big_font, centered=True)
        self.draw_text(f"Puntuación final: {self.engine.score}",
                       WIDTH // 2, 275, centered=True)
        self.draw_text(f"Nivel alcanzado: {self.engine.level}",
                       WIDTH // 2, 327, centered=True)
        pygame.draw.rect(self.screen, (38, 150, 75), self.restart_button,
                         border_radius=9)
        self.draw_text("JUGAR DE NUEVO (R)", WIDTH // 2,
                       self.restart_button.y + 10, centered=True)

    def handle_event(self, event):
        if event.type == pygame.QUIT:
            return False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return False
            if self.state == "menu" and event.key in (pygame.K_RETURN, pygame.K_SPACE):
                self.new_game()
            elif self.state == "over" and event.key in (pygame.K_r, pygame.K_RETURN):
                self.new_game()
            elif self.state == "playing" and event.key == pygame.K_SPACE:
                self.shoot()
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.state == "menu":
                self.new_game()
            elif self.state == "over" and self.restart_button.collidepoint(event.pos):
                self.new_game()
        return True

    def run(self):
        running = True
        while running:
            # dt real: velocidades independientes del hardware y precisión subpíxel.
            dt = min(self.clock.tick(FPS) / 1000, 0.05)
            for event in pygame.event.get():
                if not self.handle_event(event):
                    running = False
                    break
            if not running:
                break
            if self.state == "playing":
                self.update(dt)
                self.draw_game()
            elif self.state == "over":
                self.draw_game_over()
            else:
                self.draw_menu()
            pygame.display.flip()


if __name__ == "__main__":
    try:
        Game().run()
    finally:
        pygame.quit()
