import pygame
import random
import time
import os

pygame.font.init()
pygame.init()

# Multimedia
background = pygame.transform.scale(
    pygame.image.load("images/wallpaper.jpg"), (1080, 686)
)
rocket_img = pygame.transform.scale(pygame.image.load("images/rocket.png"), (64, 64))
laser_img = pygame.image.load("images/laser.png")
star_img = pygame.transform.scale(pygame.image.load("images/star.png"), (64, 64))
heart_img = pygame.transform.scale(pygame.image.load("images/heart.png"), (15, 15))

# Pantalla
fps = 30
width = background.get_width()
height = background.get_height()
window = pygame.display.set_mode((width, height))
pygame.display.set_caption("Juego - Math Invaders")

# main_font = pygame.font.SysFont("comicsans", 20)
main_font = pygame.font.Font("VT323-Regular.ttf", 30)


# Rocket
class Ship:
    def __init__(self, x, y, health=100):
        self.x = x
        self.y = y
        self.health = health
        self.ship_img = None
        self.laser_img = None
        self.cool_down_counter = 0

    def draw(self, window):
        window.blit(self.ship_img, (self.x, self.y))

    def get_width(self):
        return self.ship_img.get_width()

    def get_height(self):
        return self.ship_img.get_height()


# Jugador
class Player(Ship):
    def __init__(self, x, y, health=100):
        super().__init__(x, y, health)
        self.ship_img = rocket_img
        self.laser_img = laser_img
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.max_health = health


# Enemigos
class Enemy(Ship):
    colores = {
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

    def __init__(self, x, y, color, health=100):
        super().__init__(x, y, health)
        self.ship_img = star_img
        self.color = color
        self.mask = pygame.mask.from_surface(self.ship_img)

    def draw_enemy(self, window):
        window.blit(self.ship_img, (self.x, self.y))
        number_label = main_font.render(str(self.color), 1, self.colores[self.color])
        window.blit(
            number_label,
            (
                self.x + int(star_img.get_width() / 2) - 6,
                self.y + int(star_img.get_height() / 2) - 15,
            ),
        )

    def move(self, vel):
        self.y += vel

    def get_height(self):
        return self.ship_img.get_height()


# Corazón del juego
def main():
    run = True
    level = 0
    score = 0
    lives = 3
    player_vel = 10
    player = Player(int(width / 2), height - 66)

    enemies = []
    enemy_vel = 1

    clock = pygame.time.Clock()

    # Función que dibuja el contenido
    def redraw_window():
        window.blit(background, (0, 0))

        # Dibujar texto (vida y nivel)
        score_label = main_font.render(f"Puntuación: {score}", 1, (255, 255, 255))
        level_label = main_font.render(f"Nivel: {level}", 1, (255, 255, 255))
        life_label = main_font.render(f"Vida: {player.health}%", 1, (255, 255, 255))
        lifes_label = main_font.render(f"Vidas restantes: ", 1, (255, 255, 255))
        cord_label = main_font.render(f"x={player.x}, y={player.y}", 1, (255, 255, 255))

        window.blit(score_label, (width - score_label.get_width() - 10, 5))
        window.blit(lifes_label, (width - lifes_label.get_width() - (heart_img.get_width() + 10) * lives, 35,))
        window.blit(level_label, (10, 5))
        window.blit(life_label, (10, 35))
        window.blit(cord_label, (10, 65))
        for live in range(lives + 1):
            window.blit(
                heart_img, (width - heart_img.get_width() * live - (10 * live), 42)
            )

        # Dibujar enemigos
        for enemy in enemies:
            enemy.draw_enemy(window)
        pygame.display.update()

        # Dibujar rocket
        player.draw(window)

    # Inicia pantalla y captura controles de teclado
    while run:
        clock.tick(fps)

        if len(enemies) == 0:
            level += 1
            if level <= 3:
                ran_max = 4
            elif level <= 6 and level > 3:
                ran_max = 6
            else:
                ran_max = 10
            for i in range(level + 3):
                enemy = Enemy(
                    random.randrange(50, width - 50 - star_img.get_width()),
                    random.randrange(-500, -100),
                    random.randrange(1, ran_max),
                )
                enemies.append(enemy)

        # Cerrar ventana
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        # Eventos de teclado
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a] and player.x > 0:  # Izquierda
            player.x -= player_vel
        if keys[pygame.K_d] and player.x + player.get_width() < width:  # Derecha
            player.x += player_vel
        if keys[pygame.K_w] and player.y - 10 > 0:  # Arriba
            player.y -= player_vel
        if keys[pygame.K_s] and player.y + 10 + player.get_height() < height:  # Abajo
            player.y += player_vel

        # Movimiento de enemigos
        for enemy in enemies[:]:
            enemy.move(enemy_vel)
            if enemy.y + enemy.get_height() > height:
                player.health -= enemy.color
                enemies.remove(enemy)

        redraw_window()


main()


# https://www.youtube.com/watch?v=Q-__8Xw9KTM&ab_channel=TechWithTim
# https://www.youtube.com/watch?v=rp9s1O3iSEQ&ab_channel=LeMasterTech