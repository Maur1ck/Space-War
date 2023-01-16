import os
import sys
import pygame
import random


# функция для загрузки фотографий
def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


# настройка окна игры
pygame.init()
size = width, height = 500, 500
screen = pygame.display.set_mode(size)
pygame.display.set_caption("SpaceWar")
pygame.mouse.set_cursor(*pygame.cursors.diamond)


class Player(pygame.sprite.Sprite):
    player_image = load_image('spaceship.png')

    def __init__(self):
        super().__init__(player_group, all_sprites)
        self.image = pygame.transform.scale(Player.player_image, (75, 75))
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.rect.centerx = width // 2
        self.rect.y = height // 3 * 2
        self.health = 3
        self.shoot_delay = 250
        self.last_shot = pygame.time.get_ticks()

    # перемещение персонажа drag&drop
    def update(self):
        if moving:
            pos = pygame.mouse.get_pos()
            for player in player_group:
                self.rect.x = pos[0] - (player.rect.width / 2)
                self.rect.y = pos[1] - (player.rect.height / 2)
                self.shoot()

    # отображение жизней
    def draw_health(self):
        show = 0
        x = 20
        while show != self.health:
            screen.blit(pygame.transform.scale(Player.player_image, (20, 20)), (x, height - 30))
            x += 40
            show += 1

    # появление пули
    def shoot(self):
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.shoot_delay:
            self.last_shot = now
            Bullet(self.rect.centerx, self.rect.top)


class Enemy(pygame.sprite.Sprite):
    player_image = load_image('asteroid.png')
    sizes = [(75, 75), (50, 50), (50, 50)]

    def __init__(self):
        super().__init__(enemy_group, all_sprites)
        self.size = random.choice(Enemy.sizes)
        self.image_orig = pygame.transform.scale(Enemy.player_image, self.size)
        self.image = self.image_orig.copy()
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.rect.x = random.randrange(width - self.rect.width)
        self.rect.y = random.randrange(-100, -50)
        self.health = 1 if 50 in self.size else 3
        self.speed = random.randrange(1, 7)
        self.rot = 0
        self.rot_speed = random.randrange(-10, 10)
        self.last_update = pygame.time.get_ticks()

    def update(self):
        self.rotate()
        self.rect.y += self.speed
        if self.rect.top > height + 10:
            self.rect.x = random.randrange(width - self.rect.width)
            self.rect.y = random.randrange(-100, -50)
            self.speed = random.randrange(1, 7)

    def rotate(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > 50:
            self.last_update = now
            old_center = self.rect.center
            self.rot = (self.rot + self.rot_speed) % 360
            self.image = pygame.transform.rotate(self.image_orig, self.rot)
            self.rect = self.image.get_rect()
            self.rect.center = old_center


class Bullet(pygame.sprite.Sprite):
    bullet_image = load_image('bullet.png')

    def __init__(self, x, y):
        super().__init__(bullets_group, all_sprites)
        self.image = pygame.transform.scale(Bullet.bullet_image, (75, 75))
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.speed = -10

    def update(self):
        self.rect.y += self.speed

        # убить, если он заходит за верхнюю часть экрана
        if self.rect.bottom < 0:
            self.kill()


class AnimatedSprite(pygame.sprite.Sprite):
    def __init__(self, sheet, columns, rows, x, y):
        super().__init__(explosion_group, all_sprites)
        self.frames = []
        self.cut_sheet(sheet, columns, rows)
        self.cur_frame = 0
        self.image = pygame.transform.scale(self.frames[self.cur_frame], (50, 50))
        self.rect = self.rect.move(x, y)
        self.last_update = 0

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)))

    def update(self):
        self.last_update += 1
        if self.frames[self.cur_frame] == self.frames[-1]:
            self.kill()
        now = pygame.time.get_ticks()
        if self.last_update % 3 == 0:
            self.cur_frame = (self.cur_frame + 1) % len(self.frames)
            self.image = pygame.transform.scale(self.frames[self.cur_frame], (100, 100))


class Button(pygame.sprite.Sprite):
    def __init__(self, button_width, button_height, inactive_color, active_color):
        super().__init__(button_group, all_sprites)
        self.width = button_width
        self.height = button_height
        self.inactive_clr = inactive_color
        self.active_clr = active_color

    def draw(self, x, y, message, message_size, action=None, mouse_down=False):
        mouse = pygame.mouse.get_pos()
        if x < mouse[0] < x + self.width and y < mouse[1] < y + self.height:
            pygame.draw.rect(screen, self.active_clr, (x, y, self.width, self.height))
            if mouse_down and action is not None:
                action()
        else:
            pygame.draw.rect(screen, self.inactive_clr, (x, y, self.width, self.height))

        draw_text(screen, message, message_size, x + 10, y + 10)


# функциия для выхода из игры
def terminate():
    pygame.quit()
    sys.exit()


# стартовое окно
def start_screen():

    # установка фона игры
    fon = pygame.transform.scale(load_image('start_screen.png'), (width, height))
    screen.blit(fon, (0, 0))

    button_start = Button(165, 55, (0, 200, 255), (0, 150, 255))
    button_info = Button(50, 50, (0, 200, 255), (0, 150, 255))

    while True:
        mouse_down = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                if int(high_score) < score:
                    with open('score.txt', 'w') as f:
                        f.write(str(score))
                        f.close()
                terminate()
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_down = True

        pygame.draw.rect(screen, (0, 200, 255), (50, 35, 400, 135))
        draw_text(screen, "SPACE", 50, 160, 50)
        draw_text(screen, 'WAR', 50, 200, 110)

        button_start.draw(75, 310, "START", 40, run_game, mouse_down)
        button_info.draw(5, 445, "?", 40, info_screen, mouse_down)

        pygame.display.flip()

        clock.tick(FPS)


# окно информации
def info_screen():
    global score

    # установка фона игры
    fon = pygame.transform.scale(load_image('final_screen.jpg'), (width, height))
    screen.blit(fon, (0, 0))

    strings = ["Правила игры:", "Пролетель как можно дольше"]
    strings2 = ["Цель игры:", "Набрать как можно больше", "очков"]
    strings3 = ["Управление:", "ЛКМ"]

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                if int(high_score) < score:
                    with open('score.txt', 'w') as f:
                        f.write(str(score))
                        f.close()
                terminate()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    start_screen()

        y = 25
        for string in strings:
            draw_text(screen, str(string), 25, 10, y)
            y += 25

        y2 = 100
        for string2 in strings2:
            draw_text(screen, str(string2), 25, 10, y2)
            y2 += 25

        y3 = 200
        for string3 in strings3:
            draw_text(screen, str(string3), 25, 10, y3)
            y3 += 25

        draw_text(screen, "ESС: вернуться назад", 25, 10, 465)

        pygame.display.flip()
        clock.tick(FPS)


# финальное окно
def final_screen():
    global score, high_score

    # установка фона игры
    fon = pygame.transform.scale(load_image('final_screen.jpg'), (width, height))
    screen.blit(fon, (0, 0))

    button_restart = Button(225, 55, (0, 200, 255), (0, 150, 255))
    button_menu = Button(225, 50, (0, 200, 255), (0, 150, 255))

    while True:
        mouse_down = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                if int(high_score) < score:
                    with open('score.txt', 'w') as f:
                        f.write(str(score))
                        f.close()
                terminate()
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_down = True

        if int(score) > int(high_score):
            high_score = score

        draw_text(screen, f"Рекорд: {str(high_score)}", 50, 50, 75)
        draw_text(screen, f"Счет: {str(score)}", 50, 50, 150)

        button_restart.draw(125, 300, "RESTART", 40, run_game, mouse_down)
        button_menu.draw(125, 365, "MENU", 40, start_screen, mouse_down)

        pygame.display.flip()
        clock.tick(FPS)


# для отображения текста
def draw_text(scr, text, text_size, x, y):
    font = pygame.font.Font("minecraft.ttf", text_size)
    string_rendered = font.render(text, True, pygame.Color('white'))
    scr.blit(string_rendered, (x, y))


# группы спрайтов (персонажей)
all_sprites = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()
bullets_group = pygame.sprite.Group()
explosion_group = pygame.sprite.Group()
button_group = pygame.sprite.Group()

# настройка цикла игры
FPS = 100
clock = pygame.time.Clock()
running = True
ending = False
moving = False
score = 0
with open('score.txt', 'r') as f:
    high_score = f.read()
    f.close()


def run_game():
    global running, ending, moving, score

    for sprite in all_sprites:
        sprite.kill()

    running = True
    ending = False
    moving = False
    score = 0
    # создание игрока
    player = Player()

    # создание астероидов
    for i in range(10):
        Enemy()

    # цикл отрисовки игры
    while running:

        # запуск финального окна
        if ending:
            final_screen()

        # какие клавиши были нажаты
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                if int(high_score) < score:
                    with open('score.txt', 'w') as f:
                        f.write(str(score))
                        f.close()
                terminate()

            # если лкм
            if event.type == pygame.MOUSEBUTTONDOWN:

                # координаты мышки
                pos = pygame.mouse.get_pos()

                # проверка попадания на персонажа
                for player in player_group:
                    if player.rect.collidepoint(pos):
                        moving = True

            if event.type == pygame.MOUSEBUTTONUP:
                moving = False

        # обновление (перемещение) астероидов и пуль
        all_sprites.update()

        # проверка попала ли пуля в астероид
        for enemy in enemy_group:
            for bullet in bullets_group:
                hits = pygame.sprite.collide_mask(bullet, enemy)
                if hits:
                    AnimatedSprite(load_image("explosion.png"), 4, 4, enemy.rect.x, enemy.rect.y)
                    score += 1
                    enemy.health -= 1
                    if enemy.health == 0:
                        enemy.kill()
                        Enemy()
                    bullet.kill()

        # проверка попал ли астероид в корабль
        for enemy in enemy_group:
            hits = pygame.sprite.collide_mask(enemy, player)
            if hits:
                AnimatedSprite(load_image("explosion.png"), 4, 4, enemy.rect.x, enemy.rect.y)
                player.health -= 1
                if player.health == 0:
                    ending = True
                enemy.kill()

        # установка фона игры
        fon = pygame.transform.scale(load_image('space.png'), (width, height))
        screen.blit(fon, (0, 0))

        # отрисовка спрайтов (персонажей)
        player_group.draw(screen)
        enemy_group.draw(screen)
        bullets_group.draw(screen)
        explosion_group.draw(screen)
        draw_text(screen, str(score), 25, 425, 15)
        player.draw_health()

        # смена кадра
        pygame.display.flip()
        clock.tick(FPS)


# заставка игры
start_screen()

# заверщение игры
pygame.quit()
