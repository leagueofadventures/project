import pygame
import sys
import random
import time
import json

# Инициализация Pygame
pygame.init()

# Размеры экрана
WIDTH, HEIGHT = pygame.display.Info().current_w, pygame.display.Info().current_h
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("RPG Битва")

font = pygame.font.Font(None, 30)

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
displayed_text = ""
counter = 0
text_output = []

# --- Класс для текстового ввода ---
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
def draw_text(text, x, y, color=TEXT_COLOR, size=30, center=False):
    font_render = pygame.font.Font(None, size)
    render = font_render.render(text, True, color)
    rect = render.get_rect()
    if center:
        rect.center = (x, y)
    else:
        rect.topleft = (x, y)
    screen.blit(render, rect)

# --- Класс Героя ---
class Hero:
    def __init__(self, dmg, hp, armor, money, dodge_chance, name, level=1, exp=0, next_level_exp=100):
        self.dmg = dmg
        self.original_dmg = dmg
        self.hp = hp
        self.original_hp = hp
        self.armor = armor
        self.money = money
        self.dodge_chance = int(dodge_chance * 100)
        self.name = name
        self.level = level
        self.exp = exp
        self.next_level_exp = next_level_exp

    def level_up(self):
        if self.exp >= self.next_level_exp:
            self.level += 1
            self.next_level_exp *= 2
            self.exp = 0

            increase_amount = self.level * 0.2
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
            add_text_output(f"{self.name} достиг уровня {self.level}!")

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
        else:
            damage = self.dmg * 1.1 if is_crit else self.dmg * 0.7

        damage = int(max(1, damage - enemy.armor))
        return damage, body_part, is_crit

    def draw_health_bar(self, screen, x, y):
        bar_width = 100
        bar_height = 10
        ratio = self.hp / self.original_hp if self.original_hp > 0 else 0
        pygame.draw.rect(screen, WHITE, (x, y, bar_width, bar_height))
        pygame.draw.rect(screen, GREEN, (x, y, bar_width * ratio, bar_height))


# --- Класс Врага ---
class Enemy:
    def __init__(self, dmg, hp, armor, dodge_chance, name, crit_chance=10):
        self.name = name
        self.dmg = dmg
        self.hp = hp
        self.max_hp = hp
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
        ratio = self.hp / self.max_hp if self.max_hp > 0 else 0
        pygame.draw.rect(screen, WHITE, (x, y, bar_width, bar_height))
        pygame.draw.rect(screen, RED, (x, y, bar_width * ratio, bar_height))

# --- Функция добавления текста в журнал ---
def add_text_output(text):
    text_output.append(text)
    if len(text_output) > 7:
        text_output.pop(0)

# --- Функция боя ---
def battle(hero, enemies, enemy_index):
    global text_output
    running = True
    turn = 0
    text_output = []
    update_display = True

    current_enemy = enemies[enemy_index]
    add_text_output(f"Начинается битва против {current_enemy.name}!")

    while running:
        if update_display:
          screen.fill(BACKGROUND_COLOR)
          # Индикатор хода
          if turn == 0:
              draw_text("Ваш ход! (Нажмите SPACE для атаки)", WIDTH - 300, 30, GREEN)
          else:
              draw_text("Ход врага!", WIDTH - 200, 30, RED)

          text_y_offset = 30
          # Исправлено отображение HP: если текущее здоровье меньше или равно нулю, отображаем 0
          draw_text(f"{hero.name}: HP {max(0, hero.hp)}/{hero.original_hp} | Уровень: {hero.level} | Золото: {hero.money}", 10, text_y_offset, HERO_COLOR)
          text_y_offset += 25
          draw_text(f"Броня: {hero.armor} | Уворот: {hero.dodge_chance}%", 10, text_y_offset, HERO_COLOR)
          text_y_offset += 25
          hero.draw_health_bar(screen, 10, text_y_offset)
          text_y_offset += 15
          draw_text(f"Опыт: {hero.exp}/{hero.next_level_exp}", 10, text_y_offset, HERO_COLOR)
          text_y_offset += 40

          # Исправлено отображение HP: если текущее здоровье меньше или равно нулю, отображаем 0
          draw_text(f"{current_enemy.name}: HP {max(0, current_enemy.hp)}/{current_enemy.max_hp}", 10, text_y_offset, ENEMY_COLOR)
          text_y_offset += 25
          draw_text(f"Броня: {current_enemy.armor}", 10, text_y_offset, ENEMY_COLOR)
          text_y_offset += 25
          current_enemy.draw_health_bar(screen, 10, text_y_offset)

          # Вывод журнала боя
          y_offset = text_y_offset + 50
          draw_text("Журнал боя:", 10, y_offset - 30, WHITE, size=24)
          for line in text_output:
              draw_text(line, 10, y_offset, WHITE, size=24)
              y_offset += 20
          
          pygame.display.flip()
          update_display = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                save_game(hero, enemy_index, enemies)
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    save_game(hero, enemy_index, enemies)
                    pygame.quit()
                    sys.exit()

                if event.key == pygame.K_SPACE:
                    if turn == 0:
                        damage, part, is_crit = hero.attack(current_enemy)
                        current_enemy.hp -= damage
                        current_enemy.hp = max(0, current_enemy.hp) # Обновляем сразу после удара
                        crit_text = " (КРИТ!)" if is_crit else ""
                        add_text_output(f"{hero.name} ударил {current_enemy.name} по {part} на {damage} урона{crit_text}!")
                        turn = 1
                        update_display = True
                        save_game(hero, enemy_index, enemies)  # Сохраняем состояние после хода героя

                if current_enemy.hp <= 0:
                    add_text_output(f"{current_enemy.name} повержен!")
                    hero.gain_experience_and_gold(50, 15)
                    hero.restore_health()
                    current_enemy.hp = 0  # Обнуляем хитбар врага
                    enemies[enemy_index].hp = 0  # Обнуляем хитбар врага в списке врагов
                    update_display = True
                    current_enemy.draw_health_bar(screen, 10, text_y_offset)
                    save_game(hero, enemy_index, enemies)  # Сохраняем состояние после победы
                    pygame.display.flip()
                    pygame.time.wait(2000)
                    return True

        if turn == 1 and current_enemy.hp > 0:
            if random.randint(1, 100) > hero.dodge_chance:
                damage, is_enemy_crit = current_enemy.attack(hero)
                hero.hp -= damage
                hero.hp = max(0, hero.hp) # Обновляем сразу после удара
                crit_text = " (КРИТ!)" if is_enemy_crit else ""
                add_text_output(f"{current_enemy.name} нанес {hero.name} {damage} урона{crit_text}!")
            else:
                add_text_output(f"{hero.name} увернулся от атаки {current_enemy.name}!")
            turn = 0
            update_display = True
            save_game(hero, enemy_index, enemies)  # Сохраняем состояние после хода врага

        if hero.hp <= 0:
            update_display = True
            save_game(hero, enemy_index, enemies)  # Сохраняем состояние после поражения
            return False

        #pygame.display.flip()
        if turn == 1:
            pygame.time.wait(1000)

# --- Функция сохранения игры ---
def save_game(hero, enemy_index, enemies):
    data = {
        "hero": {
            "dmg": hero.original_dmg,
            "hp": hero.original_hp,
            "armor": hero.armor,
            "money": hero.money,
            "dodge_chance": hero.dodge_chance / 100,
            "name": hero.name,
            "level": hero.level,
            "exp": hero.exp,
            "next_level_exp": hero.next_level_exp,
            "current_hp": hero.hp  # Сохраняем текущее здоровье героя
        },
        "enemy_index": enemy_index,
        "enemies": [
            {
                "name": enemy.name,
                "dmg": enemy.dmg,
                "hp": enemy.hp,
                "max_hp": enemy.max_hp,
                "armor": enemy.armor,
                "dodge_chance": enemy.dodge_chance,
                "crit_chance": enemy.crit_chance
            } for enemy in enemies
        ]
    }
    with open("save_game.json", "w") as f:
        json.dump(data, f)

# --- Функция загрузки игры ---
def load_game():
    try:
        with open("save_game.json", "r") as f:
            data = json.load(f)
            hero_data = data["hero"]
            hero = Hero(
                hero_data["dmg"], 
                hero_data["hp"], 
                hero_data["armor"], 
                hero_data["money"],
                hero_data["dodge_chance"], 
                hero_data["name"], 
                hero_data["level"], 
                hero_data["exp"],
                hero_data["next_level_exp"]
            )
            hero.hp = hero_data["current_hp"]  # Загружаем текущее здоровье героя
            enemy_index = data["enemy_index"]
            enemies_data = data["enemies"]
            enemies = []
            for enemy_data in enemies_data:
                enemy = Enemy(
                    enemy_data["dmg"],
                    enemy_data["max_hp"],  # Используем max_hp для инициализации
                    enemy_data["armor"],
                    enemy_data["dodge_chance"],
                    enemy_data["name"],
                    enemy_data["crit_chance"]
                )
                enemy.hp = enemy_data["hp"]  # Устанавливаем текущее здоровье
                enemies.append(enemy)
            return hero, enemy_index, enemies
    except FileNotFoundError:
        return None, 0, None

# --- Функция создания героя ---
def create_hero(class_name):
    class_name = class_name.lower()
    if class_name == "воин":
        return Hero(20, 100, 5, 0, 0.05, "Воин")
    elif class_name == "маг":
        return Hero(30, 60, 2, 0, 0.02, "Маг")
    elif class_name == "плут":
        return Hero(25, 80, 3, 0, 0.10, "Плут")
    return None
            
# --- Главная функция ---
def main():
    global displayed_text
    hero, enemy_index, enemies = load_game()

    if enemies is None:
        enemies = [
            Enemy(13, 45, 4, 2, "Бандит", crit_chance=5),
            Enemy(20, 60, 8, 5, "Паладин", crit_chance=10),
            Enemy(18, 40, 2, 10, "Паук", crit_chance=20)
        ]

    if hero is None:
        game_state = "class_selection"
    else:
        game_state = "battle"

    while True:
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                save_game(hero, enemy_index, enemies)
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    save_game(hero, enemy_index, enemies)
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
                    displayed_text = ""
                    save_game(hero, enemy_index, enemies)  # Сохраняем после выбора класса
                else:
                    add_text_output("Некорректный выбор. Попробуйте снова.")

        elif game_state == "battle":
            if not battle(hero, enemies, enemy_index):
                draw_text("Вы проиграли. Нажмите любую клавишу для выхода.", WIDTH // 2, HEIGHT // 2 + 100, RED, center=True)
                pygame.display.flip()
                waiting_for_key = True
                while waiting_for_key:
                    for event in pygame.event.get():
                        if event.type == pygame.KEYDOWN or event.type == pygame.QUIT:
                            save_game(hero, enemy_index, enemies)
                            pygame.quit()
                            sys.exit()
            else:
                enemy_index = (enemy_index + 1) % len(enemies)
                if enemy_index == 0:
                    game_state = "victory"
                save_game(hero, enemy_index, enemies)  # Сохраняем после каждой битвы

        elif game_state == "victory":
            draw_text("Поздравляем! Вы победили всех врагов!", WIDTH // 2, HEIGHT // 2, GREEN, center=True)
            draw_text("Нажмите Enter, чтобы играть снова.", WIDTH // 2, HEIGHT // 2 + 50, WHITE, center=True)

            for event in events:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        hero = None
                        enemy_index = 0
                        enemies = [
                            Enemy(13, 45, 4, 2, "Бандит", crit_chance=5),
                            Enemy(20, 60, 8, 5, "Паладин", crit_chance=10),
                            Enemy(18, 40, 2, 10, "Паук", crit_chance=20)
                        ]
                        game_state = "class_selection"
                        text_output = []
                        save_game(hero, enemy_index, enemies)  # Сохраняем состояние новой игры

        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    main()
