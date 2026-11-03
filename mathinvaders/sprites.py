"""Sprites y movimiento con coordenadas decimales y tiempo por fotograma."""

import random

import pygame


class Player(pygame.sprite.Sprite):
    def __init__(self, image, width, height, speed=310):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect(midbottom=(width // 2, height - 20))
        self.position = pygame.Vector2(self.rect.topleft)
        self.width = width
        self.height = height
        self.speed = speed

    def update(self, dt):
        keys = pygame.key.get_pressed()
        direction = pygame.Vector2(
            int(keys[pygame.K_d]) - int(keys[pygame.K_a]),
            int(keys[pygame.K_s]) - int(keys[pygame.K_w]),
        )
        if direction.length_squared() > 1:
            direction.normalize_ip()
        self.position += direction * self.speed * dt
        self.position.x = max(0, min(self.width - self.rect.width, self.position.x))
        self.position.y = max(0, min(self.height - self.rect.height, self.position.y))
        self.rect.topleft = (round(self.position.x), round(self.position.y))


class Laser(pygame.sprite.Sprite):
    def __init__(self, image, centerx, bottom, speed=640):
        super().__init__()
        self.image = image
        self.rect = image.get_rect(centerx=centerx, bottom=bottom)
        self.y = float(self.rect.y)
        self.speed = speed

    def update(self, dt):
        self.y -= self.speed * dt
        self.rect.y = round(self.y)
        if self.rect.bottom < 0:
            self.kill()


class Star(pygame.sprite.Sprite):
    def __init__(self, image, number_font, number, slot, total, width, height,
                 level, fast=False, rng=None):
        super().__init__()
        self.number = number
        self.slot = slot
        self.fast = fast
        self.height = height
        self.rng = rng or random.Random()
        self.image = image.copy()
        label = number_font.render(str(number), True, (255, 255, 255))
        # Contorno oscuro para legibilidad sobre la textura de la estrella.
        outline = number_font.render(str(number), True, (20, 20, 36))
        target = outline.get_rect(center=(self.image.get_width() // 2,
                                          self.image.get_height() // 2))
        for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            self.image.blit(outline, target.move(dx, dy))
        self.image.blit(label, target)
        centerx = width * (slot + 1) // (total + 1)
        self.rect = self.image.get_rect(centerx=centerx)
        self.rect.y = self.rng.randint(-280, -60)
        self.y = float(self.rect.y)
        self.speed = (70 + (level - 1) * 6) * (2.2 if fast else 1.0)

    def update(self, dt):
        self.y += self.speed * dt
        self.rect.y = round(self.y)
        if self.rect.top > self.height + 10:
            # No cambia de número: siempre sigue disponible la respuesta correcta.
            self.y = float(self.rng.randint(-250, -70))
            self.rect.y = round(self.y)
