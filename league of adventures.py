import pygame
import sys
import random
import time

# Инициализация Pygame
pygame.init()

# Размеры экрана
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
pygame.display.set_caption("RPG Битва")

# Основные цвета (RGB)
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
        self.dodge_chance = int(dodge_chance * 100)  # Преобразуем в проценты и округляем
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
            self.dodge_chance += 1  # Увеличиваем шанс уворота на 1% за уровень

    def gain_experience_and_gold(self, exp_gain, gold_gain):
        self.exp += exp_gain
        self.money += gold_gain
        self.level_up()

    def restore_health(self):
        self.hp = self.original_hp

    def attack(self, enemy):
        body_part = random.choice(['head', 'body', 'leg', 'arm'])
        crit_chance = 10 if self.name != "Плут" else 25  # У плута выше шанс крита в %
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

                    if random.randint(1, 100) > hero.dodge_chance:
                        damage, is_enemy_crit = enemy.attack(hero)
                        hero.hp -= damage
                        message += f" {enemy.name} нанес {damage} урона!"
                    else:
                        message += f" {hero.name} увернулся!"

                    if hero.hp <= 0:
                        message = "Вы проиграли. Игра окончена!"
                        running = False


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
        draw_text("Выберите класс: воин, маг, плут.", WIDTH // 2, HEIGHT // 2, WHITE, 48, center=True)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        pygame.time.wait(100)

if __name__ == "__main__":
    main()
