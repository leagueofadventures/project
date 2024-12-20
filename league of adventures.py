import pygame
import random
import time
from pygame.locals import *
from colorama import Fore, Style
import sys

# --- Инициализация Pygame ---
pygame.init()

# --- Константы окна ---
WIDTH, HEIGHT = 800, 600
FPS = 60
FONT = pygame.font.Font(None, 36)
BACKGROUND_COLOR = (20, 20, 20)
TEXT_COLOR = (255, 255, 255)
ENEMY_COLOR = (255, 50, 50)
HERO_COLOR = (50, 255, 50)

# --- Создаем экран ---
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)

input_text = ''

update_text = False

font = pygame.font.Font(None, 50)

BLACK = (0, 0, 0)

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
LIGHT_GRAY = (210, 210, 210)
DARK_GRAY = (169, 169, 169)

counter = 0

class TextInputBox(pygame.sprite.Sprite):
    def __init__(self, x, y, width, font):
        super().__init__()
        self.color = BLACK
        self.backcolor = None
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
        self.last_key_down = None

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
        self.image.fill(self.backcolor or (0, 0, 0, 0))
        for i, line in enumerate(lines):
            t_surf = self.font.render(line, True, self.color)
            self.image.blit(t_surf, (5, 5 + i * self.font.get_height()))
        pygame.draw.rect(self.image, self.color if self.active else DARK_GRAY, self.image.get_rect().inflate(-2, -2), 2)
        if self.active and self.cursor_visible:
            cursor_y = 5 + (len(lines) - 1) * self.font.get_height()
            cursor_x = 5 + self.font.size(current_line)[0]
            pygame.draw.rect(self.image, self.color, (cursor_x, cursor_y, 2, self.font.get_height()))
        self.rect = self.image.get_rect(topleft=self.pos)

    def update(self, events):
        global update_text, input_text, counter
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.rect.collidepoint(event.pos):
                    self.active = True
                else:
                    self.active = False
            if event.type == pygame.KEYDOWN and self.active:
                if event.key == pygame.K_RETURN:
                    input_text = self.text
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
                    if self.last_key_down != event.key:
                        self.text += event.unicode
                        self.render_text()
                        self.last_key_down = event.key
            if event.type == pygame.KEYUP and self.active:
                self.last_key_down = None

            if self.active:
                keys = pygame.key.get_pressed()
                if keys[pygame.K_BACKSPACE]:
                    current_time = pygame.time.get_ticks()
                    if current_time - self.backspace_timer > self.backspace_interval:
                        self.text = self.text[:-1]
                        self.render_text()
                        self.backspace_timer = current_time

        if update_text and self.active:
            self.render_text()
            update_text = False

        if counter % 20 == 0:
            self.backcolor = LIGHT_GRAY
        else:
            self.backcolor = DARK_GRAY
        self.render_text()

        current_time = pygame.time.get_ticks()
        if current_time - self.cursor_timer > 500:
            self.cursor_visible = not self.cursor_visible
            self.cursor_timer = current_time
            self.render_text()


text_input_box = TextInputBox(1000, 1300, 400, font)
group = pygame.sprite.Group(text_input_box)


# --- Функция для текста на экране ---
def draw_text(text, x, y, color=TEXT_COLOR):
    render = FONT.render(text, True, color)
    screen.blit(render, (x, y))

# --- Класс Героя ---
class Hero:
    def __init__(self, dmg, hp, armor, money, dodge_chance, name):
        self.dmg = dmg
        self.original_dmg = dmg
        self.hp = hp
        self.original_hp = hp
        self.armor = armor
        self.money = money
        self.dodge_chance = dodge_chance
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
            self.dmg = int(self.original_dmg + (self.original_dmg * increase_amount))
            self.original_dmg = self.dmg
            self.hp = int(self.original_hp + (self.original_hp * increase_amount))
            self.original_hp = self.hp
            self.armor = int(self.armor + (self.armor * increase_amount))
            self.dodge_chance += 0.001

    def gain_experience_and_gold(self, exp_gain, gold_gain):
        self.exp += exp_gain
        self.money += gold_gain
        self.level_up()

    def restore_health(self):
        self.hp = self.original_hp

    def attack(self, enemy):
        body_part = random.choice(['head', 'body', 'leg', 'arm'])
        if body_part == 'head':
            damage = max(1, self.dmg * 2 - enemy.armor)
        elif body_part == 'body':
            damage = max(1, self.dmg - enemy.armor)
        elif body_part == 'leg':
            damage = max(1, self.dmg / 1.2 - enemy.armor)
        else:
            damage = max(1, self.dmg / 1.5 - enemy.armor)
        return damage, body_part

# --- Класс Врага ---
class Enemy:
    def __init__(self, dmg, hp, armor, dodge_chance, name):
        self.name = name
        self.dmg = dmg
        self.hp = hp
        self.armor = armor
        self.dodge_chance = dodge_chance

    def attack(self, hero):
        krite = random.choice(['head', 'body'])
        if krite == 'head':
            damage = max(1, self.dmg * 2 - hero.armor)
        else:
            damage = max(1, self.dmg - hero.armor)
        return damage

# --- Функция боя ---
def battle(hero, enemy):
    clock = pygame.time.Clock()
    running = True
    message = ""
    while running:
        screen.fill(BACKGROUND_COLOR)
        draw_text(f"{hero.name}: HP {hero.hp}/{hero.original_hp}", 10, 1300, HERO_COLOR)
        draw_text(f"{enemy.name}: HP {enemy.hp}", 10, 1350, ENEMY_COLOR)
        draw_text(message, 1500, 1300)

        pygame.display.flip()
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == KEYDOWN:
                if event.key == K_SPACE:
                    damage, part = hero.attack(enemy)
                    enemy.hp -= damage
                    message = f"{hero.name} ударил по {part} на {damage} урона!"
                    if enemy.hp <= 0:
                        message = f"{enemy.name} повержен!"
                        hero.gain_experience_and_gold(50, 5)
                        hero.restore_health()
                        running = False
                        break

                    if random.random() > hero.dodge_chance:
                        damage = enemy.attack(hero)
                        hero.hp -= damage
                        message += f" {enemy.name} ответил на {damage} урона!"
                    else:
                        message += f" {hero.name} увернулся от атаки!"

                    if hero.hp <= 0:
                        message = "Вы проиграли. Игра окончена!"
                        running = False

# --- Главная программа ---
def main():
    global input_text, counter
    running = True
    clock = pygame.time.Clock()
    hero = None
    enemies = [
        Enemy(13, 35, 4, 0, "Бандит"),
        Enemy(14, 30, 0, 0, "Паладин"),
        Enemy(15, 35, 4, 0, "Паук")
    ]
    enemy_index = 0

    while running:
        screen.fill(BACKGROUND_COLOR)
        events = pygame.event.get()
        for event in events:
            if event.type == QUIT:
                running = False
            if hero is None:
                text_input_box.update(events) 

        if hero is None:
            draw_text("Выберите класс: воин, маг, плут", 10, 1300)
            group.draw(screen) 
            if input_text == 'воин':
                hero = Hero(7, 40, 12, 15, 0, "Воин")
                input_text = '' 
            elif 'маг' in input_text:
                hero = Hero(25, 15, 1, 16, 0, "Маг")
                input_text = ''
            elif 'плут' in input_text:
                hero = Hero(15, 25, 7, 38, 0.05, "Плут")
                input_text = ''
        elif enemy_index < len(enemies):
            battle(hero, enemies[enemy_index])
            if hero.hp <= 0:
                running = False
            else:
                enemy_index += 1
        else:
            draw_text("Игра завершена. Победа!", 10, 1300)

        pygame.display.flip()
        clock.tick(FPS)
        counter += 1

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
