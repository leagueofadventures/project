import pygame
import sys
import random
import time

# Инициализация Pygame
pygame.init()

# Размеры экрана (теперь FULLSCREEN)
WIDTH, HEIGHT = pygame.display.Info().current_w, pygame.display.Info().current_h
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("RPG Битва")

font = pygame.font.Font(None, 45)

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
LIGHT_GRAY = (200, 200, 200)
DARK_GRAY = (150, 150, 150)

# Переменные для обработки ввода и отображения текста
update_text = False
input_text = ""
displayed_text = ""
counter = 0  # Счетчик для смены цвета фона

class TextInputBox(pygame.sprite.Sprite):
    def __init__(self, x, y, width, font):
        super().__init__()
        self.color = BLACK
        self.backcolor = None  # Цвет фона будет меняться
        self.pos = (x, y)
        self.width = width
        self.font = font
        self.active = False
        self.text = ""
        self.render_text()
        self.backspace_timer = 0
        self.backspace_interval = 100
        self.cursor_visible = True
        self.cursor_timer = pygame.time.get_ticks()

    def render_text(self):
        words = self.text.split(' ')
        lines = []
        if words:
            current_line = words[0]
            for word in words[1:]:
                if self.font.size(current_line + ' ' + word)[0] <= self.width - 10:
                    current_line += ' ' + word
                else:
                    lines.append(current_line)
                    current_line = word
            lines.append(current_line)

        height = len(lines) * self.font.get_height() + 10
        self.image = pygame.Surface((self.width, height), pygame.SRCALPHA)
        self.image.fill(self.backcolor or (0, 0, 0, 0))  # Прозрачный фон, если backcolor не задан
        for i, line in enumerate(lines):
            t_surf = self.font.render(line, True, self.color)
            self.image.blit(t_surf, (5, 5 + i * self.font.get_height()))
        pygame.draw.rect(self.image, self.color if self.active else WHITE, self.image.get_rect().inflate(-2, -2), 2)
        if self.active and self.cursor_visible:
            cursor_y = 5 + (len(lines) - 1) * self.font.get_height()
            cursor_x = 5 + self.font.size(current_line)[0]
            pygame.draw.rect(self.image, self.color, (cursor_x, cursor_y, 2, self.font.get_height()))
        self.rect = self.image.get_rect(topleft=self.pos)

    def update(self, events):
        global update_text, input_text, displayed_text, counter
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.rect.collidepoint(event.pos):
                    self.active = True
                else:
                    self.active = False
            if event.type == pygame.KEYDOWN and self.active:
                if event.key == pygame.K_RETURN:
                    input_text = self.text
                    displayed_text = input_text
                    self.active = False
                    self.text = ""
                    self.render_text()
                    update_text = True
                elif event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                    self.render_text()
                elif event.key == pygame.K_DELETE:
                    self.text = ""
                    self.render_text()
                else:
                    self.text += event.unicode
                    self.render_text()

            if self.active:
                keys = pygame.key.get_pressed()
                if keys[pygame.K_BACKSPACE]:
                    current_time = pygame.time.get_ticks()
                    if current_time - self.backspace_timer > self.backspace_interval:
                        self.text = self.text[:-1]
                        self.render_text()
                        self.backspace_timer = current_time

        counter += 1
        if update_text and self.active:
            self.render_text()
            update_text = False

        if counter % 2 == 0:
            self.backcolor = LIGHT_GRAY
        else:
            self.backcolor = DARK_GRAY
        self.render_text()

        current_time = pygame.time.get_ticks()
        if current_time - self.cursor_timer > 500:
            self.cursor_visible = not self.cursor_visible
            self.cursor_timer = current_time
            self.render_text()

text_input_box = TextInputBox(1500, 1350, 400, font)
group = pygame.sprite.Group(text_input_box)


# Основные цвета
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
GRAY = (100, 100, 100)

# Цвета для персонажей и интерфейса
TEXT_COLOR = WHITE
HERO_COLOR = BLUE
ENEMY_COLOR = RED
BACKGROUND_COLOR = BLACK

# Частота обновления экрана
FPS = 60
clock = pygame.time.Clock()

# --- Функция для отрисовки текста ---
def draw_text(text, x, y, color=TEXT_COLOR, size=36, center=False):
    font = pygame.font.Font(None, size)
    render = font.render(text, True, color)
    rect = render.get_rect()
    if center:
        rect.center = (x, y)
    else:
        rect.topleft = (x, y)
    screen.blit(render, rect)


# --- Класс Героя ---
class Hero:
    def __init__(self, dmg, hp, armor, money, dodge_chance, name):
        self.dmg = dmg
        self.original_dmg = dmg
        self.hp = hp
        self.original_hp = hp
        self.armor = armor
        self.money = money
        self.dodge_chance = int(dodge_chance * 100)
        self.name = name
        self.level = 1
        self.exp = 0
        self.next_level_exp = 100

    def level_up(self):
        if self.exp >= self.next_level_exp:
            self.level += 1
            self.next_level_exp *= 2
            self.exp = 0

            increase_amount = self.level * 0.2
            # Балансировка классов
            if self.name == "Воин":
                self.dmg = int(self.original_dmg + (self.original_dmg * increase_amount * 0.7))
                self.hp = int(self.original_hp + (self.original_hp * increase_amount * 1.2))
                self.armor = int(self.armor + (self.armor * increase_amount * 0.8))
            elif self.name == "Маг":
                self.dmg = int(self.original_dmg + (self.original_dmg * increase_amount * 1.3))
                self.hp = int(self.original_hp + (self.original_hp * increase_amount * 0.7))
                self.armor = int(self.armor + (self.armor * increase_amount * 0.5))
            elif self.name == "Плут":
                self.dmg = int(self.original_dmg + (self.original_dmg * increase_amount))
                self.hp = int(self.original_hp + (self.original_hp * increase_amount))
                self.armor = int(self.armor + (self.armor * increase_amount * 0.6))

            self.original_dmg = self.dmg
            self.original_hp = self.hp
            self.dodge_chance += 1

    def gain_experience_and_gold(self, exp_gain, gold_gain):
        self.exp += exp_gain
        self.money += gold_gain
        self.level_up()

    def restore_health(self):
        self.hp = self.original_hp

    def attack(self, enemy):
        body_part = random.choice(['head', 'body', 'leg', 'arm'])
        crit_chance = 10 if self.name != "Плут" else 25
        is_crit = random.randint(1, 100) <= crit_chance

        if body_part == 'head':
            damage = self.dmg * 2 if is_crit else self.dmg * 1.5
        elif body_part == 'body':
            damage = self.dmg * 1.5 if is_crit else self.dmg
        elif body_part == 'leg':
            damage = self.dmg * 1.2 if is_crit else self.dmg * 0.8
        else:  # arm
            damage = self.dmg * 1.1 if is_crit else self.dmg * 0.7

        damage = int(max(1, damage - enemy.armor))
        return damage, body_part, is_crit


# --- Класс Врага ---
class Enemy:
    def __init__(self, dmg, hp, armor, dodge_chance, name, crit_chance=10):
        self.name = name
        self.dmg = dmg
        self.hp = hp
        self.armor = armor
        self.dodge_chance = dodge_chance
        self.crit_chance = crit_chance

    def attack(self, hero):
        is_crit = random.randint(1, 100) <= self.crit_chance
        damage = self.dmg * 2 if is_crit else self.dmg
        damage = int(max(1, damage - hero.armor))
        return damage, is_crit


# --- Функция боя ---
def battle(hero, enemy):
    running = True
    message = ""
    while running:
        screen.fill(BACKGROUND_COLOR)
        draw_text(f"{hero.name}: HP {hero.hp}/{hero.original_hp}, Уровень: {hero.level}, Деньги: {hero.money}, Опыт: {hero.exp}/{hero.next_level_exp}, Шанс уворота: {hero.dodge_chance}%", 10, 30, HERO_COLOR)
        draw_text(f"{enemy.name}: HP {enemy.hp}", 10, 80, ENEMY_COLOR)
        draw_text(message, WIDTH // 2, HEIGHT // 2, WHITE, size=48, center=True)

        pygame.display.flip()
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    damage, part, is_hero_crit = hero.attack(enemy)
                    enemy.hp -= damage
                    message = f"{hero.name} ударил по {part} на {damage} урона!"
                    if enemy.hp <= 0:
                        message = f"{enemy.name} повержен!"
                        hero.gain_experience_and_gold(50, 15)
                        hero.restore_health()
                        running = False
                        break

                    if random.randint(1, 100) > hero.dodge_chance:
                        damage, is_enemy_crit = enemy.attack(hero)
                        hero.hp -= damage
                        message += f" {enemy.name} нанес {damage} урона!"
                    else:
                        message += f" {hero.name} увернулся!"

                    if hero.hp <= 0:
                        message = "Вы проиграли. Игра окончена!"
                        running = False
                        break

                    if enemy.hp <=0:
                        message = 'Вы победили!'
                        

# --- Главная программа ---
def main():
    hero = None
    enemies = [
        Enemy(13, 45, 4, 2, "Бандит", crit_chance=5),
        Enemy(20, 60, 8, 5, "Паладин", crit_chance=10),
        Enemy(18, 40, 2, 10, "Паук", crit_chance=20)
    ]
    enemy_index = 0

    while True:
        screen.fill(BACKGROUND_COLOR)
        draw_text("Выберите класс: воин, маг, плут.", 400, 1350, WHITE, 48, center=True)
        group.draw(screen)
        group.update(pygame.event.get())
        pygame.display.flip()

        if displayed_text:
            if displayed_text.lower() == "воин":
                hero = Hero(20, 100, 5, 0, 0.05, "Воин")
            elif displayed_text.lower() == "маг":
                hero = Hero(30, 60, 2, 0, 0.02, "Маг")
            elif displayed_text.lower() == "плут":
                hero = Hero(25, 80, 3, 0, 0.10, "Плут")
            else:  # Если введено что-то некорректное
                continue  # Начинаем цикл заново

            while True: # Цикл смены противников
                if hero is not None:  # Проверка, был ли выбран герой
                     battle(hero, enemies[enemy_index])

                if hero.hp <=0:
                    draw_text("Вы проиграли. Нажмите любую клавишу для выхода.", WIDTH//2, HEIGHT//2 + 100, RED, center = True)
                    pygame.display.flip()
                    waiting_for_key = True
                    while waiting_for_key:
                        for event in pygame.event.get():
                            if event.type == pygame.KEYDOWN or event.type == pygame.QUIT:
                                pygame.quit()
                                sys.exit()

                enemy_index = (enemy_index + 1) % len(enemies)


        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()


        clock.tick(FPS)

if __name__ == "__main__":
    main()
