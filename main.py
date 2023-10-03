import pygame
import random

pygame.font.init()
pygame.mixer.init()
pygame.init()

# Multimedia
BACKGROUND = pygame.transform.scale(
    pygame.image.load("images/wallpaper.jpg"), (1080, 686)
)
ROCKET_IMG = pygame.transform.scale(pygame.image.load("images/rocket.png"), (72, 72))
LASER_IMG = pygame.transform.scale(pygame.image.load("images/laser.png"), (16, 32))
STAR_IMG = pygame.transform.scale(pygame.image.load("images/star.png"), (64, 64))
HEART_IMG = pygame.transform.scale(pygame.image.load("images/heart.png"), (15, 15))

EQUALS_IMG = pygame.transform.scale(pygame.image.load("images/igual.png"), (96, 96))

MAS_IMG = pygame.transform.scale(pygame.image.load("images/mas.png"), (96, 96))
MENOS_IMG = pygame.transform.scale(pygame.image.load("images/menos.png"), (96, 96))

RECTANGULO_IMG = pygame.transform.scale(
    pygame.image.load("images/rectangulo3.png"), (96, 96)
)

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# Ventana
WIDTH = BACKGROUND.get_width()
HEIGHT = BACKGROUND.get_height()
WINDOW = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Juego - Math Invaders")
CLOCK = pygame.time.Clock()
FPS = 60

# main_font = pygame.font.SysFont("comicsans", 20)
MAIN_FONT = pygame.font.Font("VT323-Regular.ttf", 30)
ALERT_FONT = pygame.font.Font("VT323-Regular.ttf", 120)


# Etiquetas
def labels(surface, text, x, y):
    font = MAIN_FONT
    text_surface = font.render(text, True, WHITE)
    text_rect = text_surface.get_rect()
    text_rect.topleft = (x - text_surface.get_width(), y)
    surface.blit(text_surface, text_rect)


# Creando estrellas
def creando_estrellas(cantidad):
    for i in range(cantidad):  # Creando las estrellas
        stars = Star(random.randint(1, 10))
        all_sprites.add(stars)
        star_list.add(stars)


class Number(pygame.sprite.Sprite):
    def __init__(self, valor):
        super().__init__()
        self.valor = valor
        self.image = pygame.transform.scale(
            pygame.image.load("images/" + self.valor + ".png"), (64, 64)
        )


class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = ROCKET_IMG
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.rect.centerx = WIDTH // 2
        self.rect.bottom = HEIGHT - 20
        self.speed_x = 0
        self.speed_y = 0
        self.speed = 5
        self.lifes = 3
        self.score = 0
        self.level = 0

    def update(self):
        self.speed_x = 0
        self.speed_y = 0
        keystate = pygame.key.get_pressed()
        if keystate[pygame.K_a]:
            self.speed_x = -self.speed
        if keystate[pygame.K_d]:
            self.speed_x = self.speed
        if keystate[pygame.K_s]:
            self.speed_y = self.speed
        if keystate[pygame.K_w]:
            self.speed_y = -self.speed

        self.rect.x += self.speed_x
        self.rect.y += self.speed_y

        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
        if self.rect.left < 0:
            self.rect.left = 0

        if self.rect.bottom > HEIGHT:
            self.rect.bottom = HEIGHT
        if self.rect.top < 0:
            self.rect.top = 0

    def shoot(self):
        laser = Laser(self.rect.centerx, self.rect.top)
        all_sprites.add(laser)
        lasers.add(laser)


class Laser(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = LASER_IMG
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.rect.y = y
        self.rect.centerx = x
        self.speedy = -10

    def update(self):
        self.rect.y += self.speedy
        if self.rect.bottom < 0:
            self.kill()


class Star(pygame.sprite.Sprite):
    COLOR = {
        1: "#FFBA08",
        2: "#FAA307",
        3: "#F48C06",
        4: "#E85D04",
        5: "#DC2F02",
        6: "#D00000",
        7: "#9D0208",
        8: "#6A040F",
        9: "#370617",
        10: "#03071E",
    }

    def __init__(self, number):
        super().__init__()
        self.image = STAR_IMG
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.rect.x = random.randrange(50, WIDTH - self.rect.width - 50)
        self.rect.y = random.randrange(-400, -20)
        self.speed = 1
        self.number = number
        self.number_label = MAIN_FONT.render(
            str(number), 1, self.COLOR[number]
        )

    def update(self):
        self.rect.y += self.speed
        WINDOW.blit(
            self.number_label,
            (
                self.rect.centerx - self.number_label.get_width() / 2,
                self.rect.centery - self.number_label.get_height() / 2,
            ),
        )

        if (
            self.rect.top > HEIGHT + 10
            or self.rect.left < -25
            or self.rect.right > WIDTH + 25
        ):
            self.rect.x = random.randrange(WIDTH - self.rect.width - 20)
            self.rect.y = random.randrange(-800, -50)
            self.speedy = 1
            self.number = new_number = random.randint(1, 10)
            self.number_label = MAIN_FONT.render(
                str(new_number), 1, self.COLOR[new_number]
            )


all_sprites = pygame.sprite.Group()  # Todo el contenido del juego
star_list = pygame.sprite.Group()  # Las estrellas
lasers = pygame.sprite.Group()  # Los Lasers

player = Player()  # Creando el jugador


all_sprites.add(player)  # Agregando jugador al grupo de sprites


def main():
    run = True
    lost = False
    number_a = Number(str(random.randint(1, 5)))
    number_b = Number(str(random.randint(1, 5)))
    result = int(number_a.valor) + int(number_b.valor)
    while run:
        CLOCK.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    player.shoot()

        if lost:
            pass
        else:
            all_sprites.update()

            # Colision estrella vs laser
            colisions = pygame.sprite.groupcollide(star_list, lasers, True, True)
            for colision in colisions:
                if colision.number == result:
                    player.score += colision.number * player.level
                else:
                    player.score -= colision.number // 2

            # Colision de jugador vs estrella
            colision = pygame.sprite.spritecollide(player, star_list, True)
            if colision:
                player.lifes -= 1

        WINDOW.blit(BACKGROUND.convert(), [0, 0])

        all_sprites.draw(WINDOW)

        star_list.update()
        if len(star_list) == 0:
            creando_estrellas(5)
            number_a = Number(str(random.randint(1, 5)))
            number_b = Number(str(random.randint(1, 5)))
            result = int(number_a.valor) + int(number_b.valor)
            player.level += 1

        if player.lifes == 0:
            lost = True
            lost_label = ALERT_FONT.render("GAME OVER", 1, WHITE)
            WINDOW.blit(
                lost_label,
                (
                    WIDTH / 2 - lost_label.get_width() / 2,
                    HEIGHT / 2 - lost_label.get_height() / 2,
                ),
            )

        # Etiquetas
        labels(WINDOW, f"Level: {str(player.level)}", WIDTH - 15, 10)
        labels(WINDOW, f"Score: {str(player.score)}", WIDTH - 15, 40)

        # Dibujar corazones
        for live in range(player.lifes + 1):
            WINDOW.blit(
                HEART_IMG, (WIDTH - HEART_IMG.get_width() * live - (15 * live), 75)
            )

        # Dibujar cuadros para operación matemática
        WINDOW.blit(RECTANGULO_IMG, (10, 10))
        WINDOW.blit(MAS_IMG, (116, 10))
        WINDOW.blit(RECTANGULO_IMG, (222, 10))
        WINDOW.blit(EQUALS_IMG, (328, 10))
        WINDOW.blit(
            number_a.image,
            (
                10 + RECTANGULO_IMG.get_width() / 2 - 32,
                10 + RECTANGULO_IMG.get_height() / 2 - 32,
            ),
        )
        WINDOW.blit(
            number_b.image,
            (
                222 + RECTANGULO_IMG.get_width() / 2 - 32,
                10 + RECTANGULO_IMG.get_height() / 2 - 32,
            ),
        )

        pygame.display.flip()


main()
