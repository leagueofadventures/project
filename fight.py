import pygame
import sys
import random
import time

# Инициализация Pygame
pygame.init()

# Размеры экрана
WIDTH, HEIGHT = pygame.display.Info().current_w, pygame.display.Info().current_h
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("RPG Битва")

font = pygame.font.Font(None, 45)

# Цвета
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
LIGHT_GRAY = (200, 200, 200)
DARK_GRAY = (150, 150, 150)

# Переменные для обработки ввода
update_text = False
input_text = ""
#displayed_text = "" #Удалить. Эта переменная объявлена в main()
counter = 0
text_output = []

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
                    displayed_text = input_text  # displayed_text теперь локальная переменная
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
                elif event.unicode:
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

# Создаем экземпляр TextInputBox внизу по центру
text_input_box = TextInputBox(WIDTH // 2 - 200, HEIGHT - 100, 400, font)
group = pygame.sprite.Group(text_input_box)


# Основные цвета
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
            add_text_output(f"{self.name} достиг уровня {self.level}!")  # Добавляем сообщение

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

    def draw_health_bar(self, screen, x, y):
        bar_width = 100
        bar_height = 10
        fill = (self.hp / self.original_hp) * bar_width
        outline_rect = pygame.Rect(x, y, bar_width, bar_height)
        fill_rect = pygame.Rect(x, y, fill, bar_height)
        pygame.draw.rect(screen, GREEN, fill_rect)  # Зеленый цвет для героя
        pygame.draw.rect(screen, WHITE, outline_rect, 2)

# --- Класс Врага ---
class Enemy:
    def __init__(self, dmg, hp, armor, dodge_chance, name, crit_chance=10):
        self.name = name
        self.dmg = dmg
        self.hp = hp
        self.max_hp = hp  # Добавляем max_hp
        self.armor = armor
        self.dodge_chance = dodge_chance
        self.crit_chance = crit_chance

    def attack(self, hero):
        is_crit = random.randint(1, 100) <= self.crit_chance
        damage = self.dmg * 2 if is_crit else self.dmg
        damage = int(max(1, damage - hero.armor))
        return damage, is_crit

    def draw_health_bar(self, screen, x, y):
        bar_width = 100
        bar_height = 10
        fill = (self.hp / self.max_hp) * bar_width
        outline_rect = pygame.Rect(x, y, bar_width, bar_height)
        fill_rect = pygame.Rect(x, y, fill, bar_height)
        pygame.draw.rect(screen, RED, fill_rect)
        pygame.draw.rect(screen, WHITE, outline_rect, 2)

def add_text_output(text):
    text_output.append(text)
    if len(text_output) > 5:  # Ограничиваем количество строк до 5
        text_output.pop(0)

# --- Функция боя ---
def battle(hero, enemy):
    global text_output
    running = True
    turn = 0
    text_output = []

    while running:
        screen.fill(BACKGROUND_COLOR)
        #Индикатор хода
        if turn == 0:
            draw_text("Ваш ход!", WIDTH - 200, 30, GREEN)
        else:
            draw_text("Ход врага!", WIDTH - 200, 30, RED)

        draw_text(f"{hero.name}: HP {hero.hp}/{hero.original_hp} | Уровень: {hero.level} | Золото: {hero.money}", 10, 30, HERO_COLOR)
        draw_text(f"Броня: {hero.armor} | Уворот: {hero.dodge_chance}%", 10, 60, HERO_COLOR)
        hero.draw_health_bar(screen, 10, 80)
        draw_text(f"Опыт: {hero.exp}/{hero.next_level_exp}", 10, 90, HERO_COLOR)
        draw_text(f"{enemy.name}: HP {enemy.hp}", 10, 140, ENEMY_COLOR)
        draw_text(f"Броня: {enemy.armor}", 10, 170, ENEMY_COLOR)
        enemy.draw_health_bar(screen, 10, 200)

        # Вывод журнала боя
        y_offset = 230
        for line in text_output:
            draw_text(line, 10, y_offset, WHITE)
            y_offset += 30

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:  # Добавлена проверка на K_ESCAPE
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

            elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE and turn == 0: # Добавлено and turn == 0
                if turn == 0:  # Ход игрока
                    damage, part, is_crit = hero.attack(enemy)
                    enemy.hp -= damage
                    enemy.hp = max(0, enemy.hp)
                    crit_text = " (КРИТ!)" if is_crit else ""
                    add_text_output(f"{hero.name} ударил {enemy.name} по {part} на {damage} урона{crit_text}!")
                    turn = 1  # Переход хода к врагу

                if enemy.hp <= 0:
                    add_text_output(f"{enemy.name} повержен!")
                    hero.gain_experience_and_gold(50, 15)
                    hero.restore_health()
                    pygame.display.flip()
                    pygame.time.wait(2000)
                    return True

        if turn == 1 and enemy.hp > 0:  # Ход врага
            if random.randint(1, 100) > hero.dodge_chance:
                damage, is_enemy_crit = enemy.attack(hero)
                hero.hp -= damage
                hero.hp = max(0, hero.hp)
                crit_text = " (КРИТ!)" if is_enemy_crit else ""
                add_text_output(f"{enemy.name} нанес {hero.name} {damage} урона{crit_text}!")
            else:
                add_text_output(f"{hero.name} увернулся от атаки {enemy.name}!")
            turn = 0  # Переход хода к игроку

        if hero.hp <= 0:
            return False

        pygame.display.flip()
        if turn == 1:
            pygame.time.wait(1000)

def main():
    hero = None
    enemies = [
        Enemy(13, 45, 4, 2, "Бандит", crit_chance=5),
        Enemy(20, 60, 8, 5, "Паладин", crit_chance=10),
        Enemy(18, 40, 2, 10, "Паук", crit_chance=20)
    ]
    enemy_index = 0
    game_state = "class_selection"
    displayed_text = ""  # Инициализация displayed_text

    while True:
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN: #Добавили проверку
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

        screen.fill(BACKGROUND_COLOR)

        if game_state == "class_selection":
            draw_text("Выберите класс: воин, маг, плут.", WIDTH//2, HEIGHT//2 - 100, WHITE, 48, center=True)
            group.update(events)
            group.draw(screen)
            if displayed_text:
                hero = create_hero(displayed_text)
                if hero:
                    game_state = "battle"
                    displayed_text = "" # Важно очистить displayed_text
                else:
                    add_text_output("Некорректный выбор. Попробуйте снова.")

        elif game_state == "battle":
            if not battle(hero, enemies[enemy_index]):
                draw_text("Вы проиграли. Нажмите любую клавишу для выхода.", WIDTH // 2, HEIGHT // 2 + 100, RED, center=True)
                pygame.display.flip()
                waiting_for_key = True
                while waiting_for_key:
                    for event in pygame.event.get():
                        if event.type == pygame.KEYDOWN or event.type == pygame.QUIT:
                            pygame.quit()
                            sys.exit()
            else:
                enemy_index = (enemy_index + 1) % len(enemies)
                if enemy_index == 0:  # If we've gone through all enemies
                    game_state = "victory"

        elif game_state == "victory":
            draw_text("Поздравляем! Вы победили всех врагов!", WIDTH // 2, HEIGHT // 2, GREEN, center=True)
            draw_text("Нажмите Enter, чтобы играть снова.", WIDTH // 2, HEIGHT // 2 + 50, WHITE, center=True)  # Добавляем инструкцию

            for event in events:  # Обрабатываем события
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        # Сбрасываем состояние игры
                        hero = None
                        enemy_index = 0
                        game_state = "class_selection"
                        text_output = []  # Очищаем журнал боя

        pygame.display.flip()
        clock.tick(FPS)

def create_hero(class_name):
    class_name = class_name.lower()
    if class_name == "воин":
        return Hero(20, 100, 5, 0, 0.05, "Воин")
    elif class_name == "маг":
        return Hero(30, 60, 2, 0, 0.02, "Маг")
    elif class_name == "плут":
        return Hero(25, 80, 3, 0, 0.10, "Плут")
    return None


if __name__ == "__main__":
    main()
