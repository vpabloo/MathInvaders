import pygame
import random
import math

# Inicialización
pygame.init()

# Constantes de configuración
CONFIG = {
    'WIDTH': 1080,
    'HEIGHT': 686,
    'FPS': 60,
    'PLAYER_SPEED': 5,
    'LASER_SPEED': -10,
    'STAR_SPEED': 1,
    'INITIAL_LIVES': 3,
    'STARS_PER_LEVEL': 5,
    'MATH_RANGE': (1, 5),
    'STAR_NUMBER_RANGE': (1, 10),
    'MIN_STAR_DISTANCE': 80,  # Distancia mínima entre estrellas
    'MAX_POSITION_ATTEMPTS': 50  # Máximo de intentos para posicionar estrella
}

# Colores
COLORS = {
    'WHITE': (255, 255, 255),
    'BLACK': (0, 0, 0),
    'STAR_COLORS': {
        1: "#FFBA08", 2: "#FAA307", 3: "#F48C06", 4: "#E85D04", 5: "#DC2F02",
        6: "#D00000", 7: "#9D0208", 8: "#6A040F", 9: "#370617", 10: "#03071E"
    }
}

# Función helper para cargar y escalar imágenes
def load_image(path, size):
    return pygame.transform.scale(pygame.image.load(f"images/{path}"), size)

# Carga de recursos
IMAGES = {
    'background': load_image("wallpaper.jpg", (CONFIG['WIDTH'], CONFIG['HEIGHT'])),
    'rocket': load_image("rocket.png", (72, 72)),
    'laser': load_image("laser.png", (16, 32)),
    'star': load_image("star.png", (64, 64)),
    'heart': load_image("heart.png", (15, 15)),
    'equals': load_image("igual.png", (96, 96)),
    'plus': load_image("mas.png", (96, 96)),
    'minus': load_image("menos.png", (96, 96)),
    'rectangle': load_image("rectangulo3.png", (96, 96))
}

# Carga de sonidos
SOUNDS = {
    'laser': pygame.mixer.Sound("sounds/lasser.wav")
}

# Configuración de ventana y fuentes
screen = pygame.display.set_mode((CONFIG['WIDTH'], CONFIG['HEIGHT']))
pygame.display.set_caption("Math Invaders")
clock = pygame.time.Clock()

main_font = pygame.font.Font("VT323-Regular.ttf", 30)
alert_font = pygame.font.Font("VT323-Regular.ttf", 100)
effect_font = pygame.font.Font("VT323-Regular.ttf", 60)

class TextEffect:
    def __init__(self, text, x, y, color, duration=60, font=None):
        self.text = text
        self.x = x
        self.y = y
        self.initial_y = y
        self.color = color
        self.duration = duration
        self.timer = 0
        self.font = font or effect_font
        self.surface = self.font.render(text, True, color)
        
    def update(self):
        self.timer += 1
        # Hacer que el texto se mueva hacia arriba y desaparezca gradualmente
        self.y = self.initial_y - (self.timer * 2)
        
        # Calcular alpha para efecto de desvanecimiento
        progress = self.timer / self.duration
        alpha = max(0, 255 * (1 - progress))
        
        # Recrear surface con nuevo alpha
        temp_surface = self.font.render(self.text, True, self.color)
        self.surface = temp_surface.copy()
        self.surface.set_alpha(alpha)
        
        return self.timer >= self.duration  # True si debe ser eliminado
    
    def render(self, screen):
        # Centrar el texto en la posición x
        x = self.x - self.surface.get_width() // 2
        screen.blit(self.surface, (x, self.y))

class Game:
    def __init__(self):
        self.all_sprites = pygame.sprite.Group()
        self.stars = pygame.sprite.Group()
        self.lasers = pygame.sprite.Group()
        self.text_effects = []  # Lista de efectos de texto temporales
        
        self.player = Player()
        self.all_sprites.add(self.player)
        
        self.current_equation = self.generate_equation()
        self.spawn_stars(CONFIG['STARS_PER_LEVEL'])
        self.need_correct_star = False  # Flag para garantizar estrella correcta
        self.game_over = False  # Estado de game over
        self.restart_button_rect = None  # Área del botón de reinicio
        
    def generate_equation(self):
        a = random.randint(*CONFIG['MATH_RANGE'])
        b = random.randint(*CONFIG['MATH_RANGE'])
        return {'a': a, 'b': b, 'result': a + b}
    
    def spawn_stars(self, count):
        # Limpiar estrellas existentes
        for star in self.stars:
            star.kill()
        self.stars.empty()
        
        # Crear estrellas con posicionamiento distribuido
        stars_to_create = []
        
        # Asegurar que al menos una estrella tenga el resultado correcto
        stars_to_create.append(self.current_equation['result'])
        
        # Crear las estrellas restantes con números aleatorios
        for _ in range(count - 1):
            stars_to_create.append(random.randint(*CONFIG['STAR_NUMBER_RANGE']))
        
        # Determinar cuántas estrellas deben ser rápidas
        fast_stars_count = self.calculate_fast_stars_count()
        
        # Crear lista de índices para estrellas rápidas (aleatoriamente)
        fast_star_indices = set()
        if fast_stars_count > 0:
            available_indices = list(range(len(stars_to_create)))
            fast_star_indices = set(random.sample(available_indices, min(fast_stars_count, len(available_indices))))
        
        # Crear estrellas con mejor distribución inicial
        for i, number in enumerate(stars_to_create):
            is_fast = i in fast_star_indices
            star = self.create_star_with_smart_positioning(number, i, count, is_fast)
            if star:
                self.all_sprites.add(star)
                self.stars.add(star)
    
    def calculate_fast_stars_count(self):
        """Calcula cuántas estrellas deben ser rápidas basado en el nivel"""
        if self.player.level < 5:
            return 0
        # Cada 5 niveles, agregar una estrella rápida más
        # Nivel 5-9: 1 estrella, 10-14: 2 estrellas, 15-19: 3 estrellas, etc.
        return (self.player.level // 5)
    
    def create_star_with_smart_positioning(self, number, index, total_stars, is_fast=False):
        """Crea una estrella con posicionamiento inteligente para evitar amontonamiento inicial"""
        star = Star(number, game=self, is_fast=is_fast)
        
        # Intentar posicionamiento distribuido en cuadrícula
        if total_stars <= 5:
            # Para pocos objetos, usar distribución horizontal
            preferred_x = (CONFIG['WIDTH'] // (total_stars + 1)) * (index + 1) - star.rect.width // 2
            preferred_x = max(50, min(CONFIG['WIDTH'] - star.rect.width - 50, preferred_x))
            
            # Y aleatoria pero en rango controlado
            preferred_y = random.randint(-300, -50)
            
            # Verificar si esta posición es válida
            temp_rect = pygame.Rect(preferred_x, preferred_y, star.rect.width, star.rect.height)
            if not star.check_collision_with_other_stars(temp_rect):
                star.rect.x = preferred_x
                star.rect.y = preferred_y
                return star
        
        # Si la distribución inteligente falla, usar el método estándar
        star.reset_position()
        return star
    
    def count_correct_stars(self):
        """Cuenta cuántas estrellas tienen el resultado correcto actualmente en pantalla"""
        return sum(1 for star in self.stars if star.number == self.current_equation['result'])
    
    def ensure_correct_star_available(self):
        """Verifica si hay estrellas con resultado correcto, si no marca que se necesita una"""
        if self.count_correct_stars() == 0:
            self.need_correct_star = True
    
    def add_text_effect(self, text, x, y, color=(255, 255, 255), duration=60):
        """Agrega un efecto de texto temporal"""
        effect = TextEffect(text, x, y, color, duration)
        self.text_effects.append(effect)
    
    def update_text_effects(self):
        """Actualiza todos los efectos de texto y elimina los expirados"""
        self.text_effects = [effect for effect in self.text_effects if not effect.update()]
    
    def render_text_effects(self):
        """Renderiza todos los efectos de texto activos"""
        for effect in self.text_effects:
            effect.render(screen)
    
    def restart_game(self):
        """Reinicia completamente el juego"""
        # Limpiar todos los sprites
        self.all_sprites.empty()
        self.stars.empty()
        self.lasers.empty()
        self.text_effects.clear()  # Limpiar efectos de texto
        
        # Reiniciar jugador
        self.player = Player()
        self.all_sprites.add(self.player)
        
        # Reiniciar ecuación y estrellas
        self.current_equation = self.generate_equation()
        self.spawn_stars(CONFIG['STARS_PER_LEVEL'])
        
        # Reiniciar flags
        self.need_correct_star = False
        self.game_over = False
        self.restart_button_rect = None
    
    def handle_collisions(self):
        # Laser vs Star collisions
        hits = pygame.sprite.groupcollide(self.stars, self.lasers, True, True)
        for star in hits:
            # Obtener posición de la estrella para mostrar el efecto
            effect_x = star.rect.centerx
            effect_y = star.rect.centery
            
            if star.number == self.current_equation['result']:
                self.player.score += star.number * max(self.player.level, 1)
                # Efecto "Correcto" en verde
                self.add_text_effect("¡CORRECTO!", effect_x, effect_y, (0, 255, 0), 90)
            else:
                self.player.score -= star.number // 2
                # Efecto "Incorrecto" en rojo
                self.add_text_effect("INCORRECTO", effect_x, effect_y, (255, 0, 0), 90)
        
        # Player vs Star collisions
        if pygame.sprite.spritecollide(self.player, self.stars, True):
            self.player.lives -= 1
        
        # Asegurar que siempre haya una estrella correcta disponible
        self.ensure_correct_star_available()
    
    def check_level_complete(self):
        if len(self.stars) == 0:
            self.player.level += 1
            # Efecto de avance de nivel en el centro de la pantalla
            center_x = CONFIG['WIDTH'] // 2
            center_y = CONFIG['HEIGHT'] // 2
            self.add_text_effect(f"¡NIVEL {self.player.level}!", center_x, center_y, (255, 215, 0), 120)
            
            self.current_equation = self.generate_equation()
            self.spawn_stars(CONFIG['STARS_PER_LEVEL'])
    
    def render_ui(self):
        # Labels
        self.render_text(f"Level: {self.player.level}", CONFIG['WIDTH'] - 15, 10, align='right')
        self.render_text(f"Score: {self.player.score}", CONFIG['WIDTH'] - 15, 40, align='right')
        
        # Lives (hearts)
        for i in range(self.player.lives):
            x = CONFIG['WIDTH'] - (IMAGES['heart'].get_width() + 15) * (i + 1)
            screen.blit(IMAGES['heart'], (x, 75))
        
        # Math equation
        positions = [(10, 10), (116, 10), (222, 10), (328, 10)]
        images = [IMAGES['rectangle'], IMAGES['plus'], IMAGES['rectangle'], IMAGES['equals']]
        
        for pos, img in zip(positions, images):
            screen.blit(img, pos)
        
        # Numbers in equation - Centrados correctamente en los rectángulos
        eq = self.current_equation
        number_a = load_image(f"{eq['a']}.png", (64, 64))
        number_b = load_image(f"{eq['b']}.png", (64, 64))
        
        # Calcular centros: rectángulo en (x,y) de 96x96, número de 64x64
        # Centro x = x_rect + (96-64)/2 = x_rect + 16
        # Centro y = y_rect + (96-64)/2 = y_rect + 16
        screen.blit(number_a, (26, 26))   # Centrado en primer rectángulo (10+16, 10+16)
        screen.blit(number_b, (238, 26))  # Centrado en segundo rectángulo (222+16, 10+16)
    
    def render_text(self, text, x, y, align='left'):
        surface = main_font.render(text, True, COLORS['WHITE'])
        if align == 'right':
            x -= surface.get_width()
        elif align == 'center':
            x -= surface.get_width() // 2
        screen.blit(surface, (x, y))
    
    def render_game_over_screen(self):
        """Renderiza la pantalla de Game Over con botón de reinicio"""
        # Fondo semi-transparente
        overlay = pygame.Surface((CONFIG['WIDTH'], CONFIG['HEIGHT']))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))
        
        # Texto "GAME OVER"
        game_over_text = alert_font.render("GAME OVER", True, COLORS['WHITE'])
        game_over_x = CONFIG['WIDTH'] // 2 - game_over_text.get_width() // 2
        game_over_y = CONFIG['HEIGHT'] // 2 - game_over_text.get_height() // 2 - 80
        screen.blit(game_over_text, (game_over_x, game_over_y))
        
        # Score final
        score_text = main_font.render(f"Score Final: {self.player.score}", True, COLORS['WHITE'])
        score_x = CONFIG['WIDTH'] // 2 - score_text.get_width() // 2
        score_y = game_over_y + game_over_text.get_height() + 20
        screen.blit(score_text, (score_x, score_y))
        
        # Level alcanzado
        level_text = main_font.render(f"Nivel Alcanzado: {self.player.level}", True, COLORS['WHITE'])
        level_x = CONFIG['WIDTH'] // 2 - level_text.get_width() // 2
        level_y = score_y + score_text.get_height() + 10
        screen.blit(level_text, (level_x, level_y))
        
        # Botón de reinicio
        button_width = 250
        button_height = 60
        button_x = CONFIG['WIDTH'] // 2 - button_width // 2
        button_y = level_y + level_text.get_height() + 40
        
        # Guardar el rectángulo del botón para detectar clics
        self.restart_button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
        
        # Dibujar botón con efecto hover
        mouse_pos = pygame.mouse.get_pos()
        button_color = (70, 180, 70) if self.restart_button_rect.collidepoint(mouse_pos) else (50, 150, 50)
        
        pygame.draw.rect(screen, button_color, self.restart_button_rect)
        pygame.draw.rect(screen, COLORS['WHITE'], self.restart_button_rect, 3)
        
        # Texto del botón
        button_text = main_font.render("JUGAR DE NUEVO", True, COLORS['WHITE'])
        text_x = button_x + button_width // 2 - button_text.get_width() // 2
        text_y = button_y + button_height // 2 - button_text.get_height() // 2
        screen.blit(button_text, (text_x, text_y))
    
    def run_frame(self):
        clock.tick(CONFIG['FPS'])
        
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE and not self.game_over:
                self.player.shoot(self.all_sprites, self.lasers)
            elif event.type == pygame.MOUSEBUTTONDOWN and self.game_over:
                # Verificar clic en botón de reinicio
                mouse_pos = pygame.mouse.get_pos()
                if self.restart_button_rect and self.restart_button_rect.collidepoint(mouse_pos):
                    self.restart_game()
                    return True  # Continuar el juego
        
        # Game over check
        if self.player.lives <= 0 and not self.game_over:
            self.game_over = True
        
        if self.game_over:
            # Actualizar efectos de texto incluso en game over
            self.update_text_effects()
            
            # Renderizar fondo del juego pero estático
            screen.blit(IMAGES['background'], (0, 0))
            self.all_sprites.draw(screen)
            
            # Render star numbers
            for star in self.stars:
                star.render_number()
            
            self.render_ui()
            self.render_text_effects()  # Renderizar efectos antes de la pantalla de game over
            
            # Renderizar pantalla de game over encima
            self.render_game_over_screen()
            pygame.display.flip()
            return True
        
        # Update game objects (solo si no es game over)
        self.all_sprites.update()
        self.handle_collisions()
        self.check_level_complete()
        self.update_text_effects()  # Actualizar efectos de texto
        
        # Render everything
        screen.blit(IMAGES['background'], (0, 0))
        self.all_sprites.draw(screen)
        
        # Render star numbers
        for star in self.stars:
            star.render_number()
        
        self.render_ui()
        self.render_text_effects()  # Renderizar efectos de texto encima de todo
        pygame.display.flip()
        return True

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = IMAGES['rocket']
        self.rect = self.image.get_rect(centerx=CONFIG['WIDTH']//2, bottom=CONFIG['HEIGHT']-20)
        self.mask = pygame.mask.from_surface(self.image)
        self.speed = CONFIG['PLAYER_SPEED']
        self.lives = CONFIG['INITIAL_LIVES']
        self.score = 0
        self.level = 0

    def update(self):
        keys = pygame.key.get_pressed()
        dx = dy = 0
        
        if keys[pygame.K_a]: dx = -self.speed
        if keys[pygame.K_d]: dx = self.speed
        if keys[pygame.K_w]: dy = -self.speed
        if keys[pygame.K_s]: dy = self.speed
        
        # Move and constrain to screen
        self.rect.x = max(0, min(CONFIG['WIDTH'] - self.rect.width, self.rect.x + dx))
        self.rect.y = max(0, min(CONFIG['HEIGHT'] - self.rect.height, self.rect.y + dy))
    
    def shoot(self, all_sprites, lasers):
        laser = Laser(self.rect.centerx, self.rect.top)
        all_sprites.add(laser)
        lasers.add(laser)
        
        # Reproducir sonido del láser
        SOUNDS['laser'].play()

class Laser(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = IMAGES['laser']
        self.rect = self.image.get_rect(centerx=x, bottom=y)
        self.mask = pygame.mask.from_surface(self.image)
        self.speed = CONFIG['LASER_SPEED']

    def update(self):
        self.rect.y += self.speed
        if self.rect.bottom < 0:
            self.kill()

class Star(pygame.sprite.Sprite):
    def __init__(self, number, game=None, is_fast=False):
        super().__init__()
        self.image = IMAGES['star']
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.game = game  # Referencia al juego para verificar resultado correcto
        self.is_fast = is_fast  # Flag para indicar si es una estrella rápida
        
        self.number = number
        # Usar color seguro: si el número está fuera del rango, usar el color del 10
        self.color = COLORS['STAR_COLORS'].get(number, COLORS['STAR_COLORS'][10])
        self.number_surface = main_font.render(str(number), True, self.color)
        
        self.reset_position()
        self.speed = self.calculate_speed()
    
    def calculate_speed(self):
        """Calcula la velocidad de la estrella basada en el nivel actual del juego"""
        base_speed = CONFIG['STAR_SPEED']
        if self.game and hasattr(self.game, 'player'):
            # Incremento muy sutil: 0.03 por nivel (apenas perceptible)
            level_bonus = self.game.player.level * 0.03
            normal_speed = base_speed + level_bonus
            
            # Si es una estrella rápida, multiplicar velocidad por 2.5
            if self.is_fast:
                return normal_speed * 2.5
            return normal_speed
        return base_speed
    
    def reset_position(self):
        margin = 50
        max_attempts = CONFIG['MAX_POSITION_ATTEMPTS']
        attempts = 0
        
        while attempts < max_attempts:
            # Generar posición aleatoria
            new_x = random.randint(margin, CONFIG['WIDTH'] - self.rect.width - margin)
            new_y = random.randint(-400, -20)
            
            # Crear rect temporal para verificar colisiones
            temp_rect = pygame.Rect(new_x, new_y, self.rect.width, self.rect.height)
            
            # Verificar colisiones con otras estrellas
            if not self.check_collision_with_other_stars(temp_rect):
                self.rect.x = new_x
                self.rect.y = new_y
                return
            
            attempts += 1
        
        # Si no se encuentra posición libre, usar posición aleatoria (fallback)
        self.rect.x = random.randint(margin, CONFIG['WIDTH'] - self.rect.width - margin)
        self.rect.y = random.randint(-400, -20)
    
    def check_collision_with_other_stars(self, temp_rect):
        """Verifica si el rect temporal colisiona con otras estrellas existentes"""
        if not self.game:
            return False
            
        min_distance = CONFIG['MIN_STAR_DISTANCE']
        temp_center = temp_rect.center
        
        for other_star in self.game.stars:
            if other_star is self:  # No verificar consigo mismo
                continue
                
            other_center = other_star.rect.center
            distance = ((temp_center[0] - other_center[0])**2 + 
                       (temp_center[1] - other_center[1])**2)**0.5
            
            if distance < min_distance:
                return True  # Hay colisión
                
        return False  # No hay colisión

    def update(self):
        self.rect.y += self.speed
        
        # Reset if off screen
        if (self.rect.top > CONFIG['HEIGHT'] + 10 or 
            self.rect.left < -25 or self.rect.right > CONFIG['WIDTH'] + 25):
            self.reset_position()
            
            # Actualizar velocidad basada en el nivel actual
            self.speed = self.calculate_speed()
            
            # Asegurar que siempre haya una estrella con el resultado correcto
            if self.game and self.game.need_correct_star:
                self.number = self.game.current_equation['result']
                self.game.need_correct_star = False
            else:
                self.number = random.randint(*CONFIG['STAR_NUMBER_RANGE'])
            
            # Usar color seguro
            self.color = COLORS['STAR_COLORS'].get(self.number, COLORS['STAR_COLORS'][10])
            self.number_surface = main_font.render(str(self.number), True, self.color)
    
    def render_number(self):
        x = self.rect.centerx - self.number_surface.get_width() // 2
        y = self.rect.centery - self.number_surface.get_height() // 2
        screen.blit(self.number_surface, (x, y))
        
        # Indicador visual para estrellas rápidas (borde rojo pulsante)
        if self.is_fast:
            # Crear efecto pulsante usando seno del tiempo
            pulse = pygame.time.get_ticks() * 0.008  # Velocidad de pulsación
            alpha = int(120 + 80 * abs(math.sin(pulse)))  # Alpha entre 120 y 200
            
            # Crear superficie temporal para el borde
            border_surface = pygame.Surface((self.rect.width + 6, self.rect.height + 6))
            border_surface.set_alpha(alpha)
            border_surface.fill((255, 80, 80))  # Rojo menos intenso para mejor visibilidad
            
            # Dibujar el borde pulsante alrededor de la estrella
            border_x = self.rect.x - 3
            border_y = self.rect.y - 3
            screen.blit(border_surface, (border_x, border_y))

def show_menu():
    while True:
        screen.blit(IMAGES['background'], (0, 0))
        title = alert_font.render("Click para iniciar...", True, COLORS['WHITE'])
        x = CONFIG['WIDTH'] // 2 - title.get_width() // 2
        screen.blit(title, (x, 350))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                return True

def main():
    if not show_menu():
        return
    
    game = Game()
    running = True
    
    while running:
        running = game.run_frame()
    
    pygame.quit()

if __name__ == "__main__":
    main()