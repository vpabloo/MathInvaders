import pygame
import random


pygame.font.init()
pygame.mixer.init()
pygame.init()

# Multimedia
BACKGROUND = pygame.transform.scale(
    pygame.image.load("images/wallpaper.jpg"), (1080, 686)
)
ROCKET_IMG = pygame.transform.scale(pygame.image.load("images/rocket.png"), (64, 64))
LASER_IMG = pygame.transform.scale(pygame.image.load("images/laser.png"), (16, 32))
STAR_IMG = pygame.transform.scale(pygame.image.load("images/star.png"), (64, 64))
HEART_IMG = pygame.transform.scale(pygame.image.load("images/heart.png"), (15, 15))

N_1_IMG = pygame.transform.scale(pygame.image.load("images/1.png"), (64, 64))
N_2_IMG = pygame.transform.scale(pygame.image.load("images/2.png"), (64, 64))
N_3_IMG = pygame.transform.scale(pygame.image.load("images/3.png"), (64, 64))
N_4_IMG = pygame.transform.scale(pygame.image.load("images/4.png"), (64, 64))
N_5_IMG = pygame.transform.scale(pygame.image.load("images/5.png"), (64, 64))
N_6_IMG = pygame.transform.scale(pygame.image.load("images/6.png"), (64, 64))
N_7_IMG = pygame.transform.scale(pygame.image.load("images/7.png"), (64, 64))
N_8_IMG = pygame.transform.scale(pygame.image.load("images/8.png"), (64, 64))
N_9_IMG = pygame.transform.scale(pygame.image.load("images/9.png"), (64, 64))
N_10_IMG = pygame.transform.scale(pygame.image.load("images/10.png"), (32, 32))

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
        self.healt = 100
        self.score = 0

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

    def __init__(self):
        super().__init__()
        self.image = STAR_IMG
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.rect.x = random.randrange(50, WIDTH - self.rect.width - 50)
        self.rect.y = random.randrange(-100, -40)
        self.speedy = random.randrange(1, 3)
        self.number = random.randint(1, 10)
        self.number_label = MAIN_FONT.render(
            str(self.number), 1, self.COLOR[self.number]
        )

    def update(self):
        self.rect.y += self.speedy
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
            self.rect.x = random.randrange(WIDTH - self.rect.width)
            self.rect.y = random.randrange(-100, -40)
            self.speedy = random.randrange(1, 3)
            player.healt -= self.number


all_sprites = pygame.sprite.Group()  # Todo el contenido del juego
star_list = pygame.sprite.Group()  # Las estrellas
lasers = pygame.sprite.Group()  # Los Lasers

player = Player()  # Creando el jugador
for i in range(5):  # Creando las estrellas
    star = Star()
    all_sprites.add(star)
    star_list.add(star)

all_sprites.add(player)  # Agregando jugador al grupo de sprites


def main():
    run = True
    while run:
        CLOCK.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    player.shoot()

        all_sprites.update()

        # Colision estrella vs laser
        colisions = pygame.sprite.groupcollide(star_list, lasers, True, True)
        for colision in colisions:
            player.score += colision.number

        # Colision de jugador vs estrella
        colision = pygame.sprite.spritecollide(player, star_list, True)
        if colision:
            player.lifes -= 1

        WINDOW.blit(BACKGROUND.convert(), [0, 0])

        all_sprites.draw(WINDOW)

        star_list.update()

        # Etiquetas
        labels(WINDOW, f"Score: {str(player.score)}", WIDTH - 15, 10)
        labels(WINDOW, f"Life: {str(player.healt)}", WIDTH - 15, 40)

        for live in range(player.lifes + 1):
            WINDOW.blit(
                HEART_IMG, (WIDTH - HEART_IMG.get_width() * live - (15 * live), 70)
            )

        WINDOW.blit(RECTANGULO_IMG, (10, 10))
        WINDOW.blit(MAS_IMG, (116, 10))
        WINDOW.blit(RECTANGULO_IMG, (222, 10))
        WINDOW.blit(EQUALS_IMG, (328, 10))

        WINDOW.blit(
            N_2_IMG,
            (
                10 + RECTANGULO_IMG.get_width() / 2 - N_1_IMG.get_width() / 2,
                10 + RECTANGULO_IMG.get_height() / 2 - N_1_IMG.get_height() / 2,
            ),
        )
        WINDOW.blit(
            N_2_IMG,
            (
                222 + RECTANGULO_IMG.get_width() / 2 - N_1_IMG.get_width() / 2,
                10 + RECTANGULO_IMG.get_height() / 2 - N_1_IMG.get_height() / 2,
            ),
        )

        pygame.display.flip()


main()
