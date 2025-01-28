import pygame
import sys
import random
import time
import json
from pygame.locals import *
from moviepy.editor import VideoFileClip

# Initialize Pygame and mixer
pygame.init()
pygame.mixer.init()

# Get screen dimensions and set display
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
WIDTH, HEIGHT = screen.get_size()
pygame.display.set_caption("RPG Битва")

# Define colors
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
LIGHT_GRAY = (200, 200, 200)
DARK_GRAY = (150, 150, 150)

# Fonts
font = pygame.font.Font(None, 30)
font_text = pygame.font.Font(None, 50)
font_text1 = pygame.font.Font(None, 35)

# Global variables for input
update_text = False
input_text = ""
displayed_text = ""
counter = 0
text_output = []

# --- TextInputBox Class ---
class TextInputBox(pygame.sprite.Sprite):
    def __init__(self, x, y, width, font, backcolor=None, border_color=BLACK):
        super().__init__()
        self.color = BLACK
        self.backcolor = backcolor
        self.pos = (x, y)
        self.width = width
        self.font = font
        self.active = False
        self.text = ""
        self.border_color = border_color
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
        pygame.draw.rect(self.image, self.border_color if self.active else WHITE, self.image.get_rect().inflate(-2, -2), 2)
        if self.active and self.cursor_visible:
            cursor_y = 5 + (len(lines) - 1) * self.font.get_height()
            cursor_x = 5 + self.font.size(current_line)[0]
            pygame.draw.rect(self.image, self.border_color, (cursor_x, cursor_y, 2, self.font.get_height()))
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

# --- Hero Class ---
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

# --- Enemy Class ---
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

# --- Function to Add Text to Battle Log ---
def add_text_output(text):
    text_output.append(text)
    if len(text_output) > 7:
        text_output.pop(0)

# --- Battle Function ---
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

            # Indicator of turn
            if turn == 0:
                draw_text("Ваш ход! (Нажмите SPACE для атаки)", WIDTH - 300, 30, GREEN)
            else:
                draw_text("Ход врага!", WIDTH - 200, 30, RED)

            text_y_offset = 30
            draw_text(f"{hero.name}: HP {max(0, hero.hp)}/{hero.original_hp} | Уровень: {hero.level} | Золото: {hero.money}", 10, text_y_offset, HERO_COLOR)
            text_y_offset += 25
            draw_text(f"Броня: {hero.armor} | Уворот: {hero.dodge_chance}%", 10, text_y_offset, HERO_COLOR)
            text_y_offset += 25
            hero.draw_health_bar(screen, 10, text_y_offset)
            text_y_offset += 15
            draw_text(f"Опыт: {hero.exp}/{hero.next_level_exp}", 10, text_y_offset, HERO_COLOR)
            text_y_offset += 40

            draw_text(f"{current_enemy.name}: HP {max(0, current_enemy.hp)}/{current_enemy.max_hp}", 10, text_y_offset, ENEMY_COLOR)
            text_y_offset += 25
            draw_text(f"Броня: {current_enemy.armor}", 10, text_y_offset, ENEMY_COLOR)
            text_y_offset += 25
            current_enemy.draw_health_bar(screen, 10, text_y_offset)

            # Battle log
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
                        current_enemy.hp = max(0, current_enemy.hp)
                        crit_text = " (КРИТ!)" if is_crit else ""
                        add_text_output(f"{hero.name} ударил {current_enemy.name} по {part} на {damage} урона{crit_text}!")
                        turn = 1
                        update_display = True
                        save_game(hero, enemy_index, enemies)

                if current_enemy.hp <= 0:
                    add_text_output(f"{current_enemy.name} повержен!")
                    hero.gain_experience_and_gold(50, 15)
                    hero.restore_health()
                    current_enemy.hp = 0
                    enemies[enemy_index].hp = 0
                    update_display = True
                    save_game(hero, enemy_index, enemies)
                    pygame.display.flip()
                    pygame.time.wait(2000)
                    return True

        if turn == 1 and current_enemy.hp > 0:
            if random.randint(1, 100) > hero.dodge_chance:
                damage, is_enemy_crit = current_enemy.attack(hero)
                hero.hp -= damage
                hero.hp = max(0, hero.hp)
                crit_text = " (КРИТ!)" if is_enemy_crit else ""
                add_text_output(f"{current_enemy.name} нанес {hero.name} {damage} урона{crit_text}!")
            else:
                add_text_output(f"{hero.name} увернулся от атаки {current_enemy.name}!")
            turn = 0
            update_display = True
            save_game(hero, enemy_index, enemies)

        if hero.hp <= 0:
            update_display = True
            save_game(hero, enemy_index, enemies)
            return False

        if turn == 1:
            pygame.time.wait(1000)

# --- Function to Draw Text ---
def draw_text(text, x, y, color=WHITE, size=30, center=False):
    font_render = pygame.font.Font(None, size)
    render = font_render.render(text, True, color)
    rect = render.get_rect()
    if center:
        rect.center = (x, y)
    else:
        rect.topleft = (x, y)
    screen.blit(render, rect)

# --- Save Game Function ---
def save_game(hero, enemy_index, enemies):
    if hero is None or enemies is None:
        return
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
            "current_hp": hero.hp
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
    with open("save_game.json", "w", encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# --- Load Game Function ---
def load_game():
    try:
        with open("save_game.json", "r", encoding='utf-8') as f:
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
            hero.hp = hero_data["current_hp"]
            enemy_index = data["enemy_index"]
            enemies_data = data["enemies"]
            enemies = []
            for enemy_data in enemies_data:
                enemy = Enemy(
                    enemy_data["dmg"],
                    enemy_data["max_hp"],
                    enemy_data["armor"],
                    enemy_data["dodge_chance"],
                    enemy_data["name"],
                    enemy_data["crit_chance"]
                )
                enemy.hp = enemy_data["hp"]
                enemies.append(enemy)
            return hero, enemy_index, enemies
    except FileNotFoundError:
        return None, 0, None

# --- Create Hero Function ---
def create_hero(class_name):
    class_name = class_name.lower()
    if class_name == "воин":
        return Hero(20, 100, 5, 0, 0.05, "Воин")
    elif class_name == "маг":
        return Hero(30, 60, 2, 0, 0.02, "Маг")
    elif class_name == "плут":
        return Hero(25, 80, 3, 0, 0.10, "Плут")
    return None

# --- Function to Add Text Output ---
def add_text_output(text):
    text_output.append(text)
    if len(text_output) > 7:
        text_output.pop(0)

# --- Function to Draw Menu ---
def draw_menu():
    screen.fill(BACKGROUND_COLOR)
    # Display background images or menu elements here
    # Example:
    if menu_image:
        screen.blit(menu_image, menu_image_rect)
    draw_text("Главное Меню", WIDTH // 2, HEIGHT // 2 - 100, WHITE, 48, center=True)
    draw_text("Нажмите 1 чтобы играть", WIDTH // 2, HEIGHT // 2, WHITE, 36, center=True)
    draw_text("Нажмите 2 чтобы зайти в настройки", WIDTH // 2, HEIGHT // 2 + 50, WHITE, 36, center=True)

# --- Function to Draw Settings ---
def draw_settings():
    screen.fill(BACKGROUND_COLOR)
    # Display settings images or elements here
    draw_text("Настройки", WIDTH // 2, HEIGHT // 2 - 100, WHITE, 48, center=True)
    draw_text("Нажмите 4 чтобы вернуться в меню", WIDTH // 2, HEIGHT // 2, WHITE, 36, center=True)

# --- Function to Draw Victory Screen ---
def draw_victory():
    screen.fill(BACKGROUND_COLOR)
    draw_text("Поздравляем! Вы победили всех врагов!", WIDTH // 2, HEIGHT // 2, GREEN, 48, center=True)
    draw_text("Нажмите Enter, чтобы играть снова.", WIDTH // 2, HEIGHT // 2 + 50, WHITE, 36, center=True)

# --- Background Color ---
BACKGROUND_COLOR = BLACK
HERO_COLOR = BLUE
ENEMY_COLOR = RED

# --- Load Images and Audio ---
def load_resources():
    resources = {}
    try:
        resources["image"] = pygame.image.load("1.png")
        resources["settings_image"] = pygame.image.load('Settings.png')
        resources["menu_image"] = pygame.image.load('menu.jpg')
        resources["second_image"] = pygame.image.load('2.png')
        pygame.mixer.music.load('12.mp3')
        resources["image_blur"] = pygame.image.load('1.blur.png')
        resources["third_image"] = pygame.image.load('3.png')
        resources["third_image_blur"] = pygame.image.load('3.blur.png')
        resources["second_image_blur"] = pygame.image.load('2.blur.png')
        resources["fourth_image"] = pygame.image.load('4.png')
        resources["fourth_image_blur"] = pygame.image.load('4.blur.png')
        resources["fifth_image"] = pygame.image.load('5.jpg')
        resources["fifth_image_blur"] = pygame.image.load('5.blur.jpg')
        resources["sixth_image"] = pygame.image.load('6.jpg')
        resources["sixth_image_blur"] = pygame.image.load('6.blur.jpg')
        resources["seventh_image"] = pygame.image.load('7.jpg')
        resources["seventh_image_blur"] = pygame.image.load('7.blur.png')
        resources["eighth_image"] = pygame.image.load('8.jpg')
        resources["eighth_image_blur"] = pygame.image.load('8.blur.png')
    except pygame.error:
        print("Не удалось загрузить одно из изображений или аудио.")
        resources = {}
    return resources

resources = load_resources()

# --- Load Video ---
def load_video():
    try:
        clip = VideoFileClip('video.mp4')
        video_width, video_height = clip.size
        return clip, video_width, video_height
    except Exception as e:
        print("Не удалось загрузить видео:", e)
        return None, 0, 0

clip, video_width, video_height = load_video()

# --- Get Rects for Images ---
if resources.get("settings_image"):
    settings_image_rect = resources["settings_image"].get_rect()
if resources.get("third_image_blur"):
    third_image_blur_rect = resources["third_image_blur"].get_rect()
if resources.get("third_image"):
    third_image_rect = resources["third_image"].get_rect()
if resources.get("image"):
    image_rect = resources["image"].get_rect()
if resources.get("second_image"):
    second_image_rect = resources["second_image"].get_rect()
if resources.get("menu_image"):
    menu_image_rect = resources["menu_image"].get_rect()
if resources.get("image_blur"):
    image_blur_rect = resources["image_blur"].get_rect()
if resources.get("second_image_blur"):
    second_image_blur_rect = resources["second_image_blur"].get_rect()

# --- Create Text Surfaces (Example) ---
# You can create and position additional text surfaces as needed
# Example:
# text_surface1 = font_text.render('Some story text...', True, BLACK)
# text_rect1 = text_surface1.get_rect(topleft=(10, 1300))

# --- Create TextInputBox Instances ---
text_input_box_menu = TextInputBox(WIDTH // 2 - 200, HEIGHT // 2 + 100, 400, font, backcolor=LIGHT_GRAY, border_color=WHITE)
text_input_box_class = TextInputBox(WIDTH // 2 - 200, HEIGHT // 2 + 200, 400, font, backcolor=LIGHT_GRAY, border_color=WHITE)
group = pygame.sprite.Group(text_input_box_menu, text_input_box_class)

# Hide class selection input initially
text_input_box_class.active = False

# --- Game States ---
# Possible states: menu, settings, class_selection, battle, victory, game_over
def main():
    global displayed_text
    clock = pygame.time.Clock()
    FPS = 60

    # Load or initialize game data
    hero, enemy_index, enemies = load_game()

    if enemies is None:
        enemies = [
            Enemy(13, 45, 4, 2, "Бандит", crit_chance=5),
            Enemy(20, 60, 8, 5, "Паладин", crit_chance=10),
            Enemy(18, 40, 2, 10, "Паук", crit_chance=20)
        ]

    if hero is None:
        game_state = "menu"
    else:
        game_state = "battle"

    # Play background music
    if resources.get("12.mp3"):
        pygame.mixer.music.play(-1)

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

        if game_state == "menu":
            draw_menu()
            group.update(events)
            text_input_box_menu.update(events)
            group.draw(screen)

            if displayed_text:
                if displayed_text == "1":
                    game_state = "class_selection"
                    displayed_text = ""
                elif displayed_text == "2":
                    game_state = "settings"
                    displayed_text = ""
                else:
                    add_text_output("Некорректный выбор. Попробуйте снова.")
                    displayed_text = ""

        elif game_state == "settings":
            draw_settings()
            # Implement settings functionalities here
            # For example, adjust volume, controls, etc.
            # Currently, just displays settings screen
            if displayed_text == "4":
                game_state = "menu"
                displayed_text = ""

        elif game_state == "class_selection":
            screen.fill(BACKGROUND_COLOR)
            draw_text("Выберите класс: воин, маг, плут.", WIDTH//2, HEIGHT//2 - 100, WHITE, 48, center=True)
            text_input_box_class.update(events)
            group.draw(screen)

            if displayed_text:
                hero = create_hero(displayed_text)
                if hero:
                    game_state = "battle"
                    displayed_text = ""
                    save_game(hero, enemy_index, enemies)
                else:
                    add_text_output("Некорректный выбор. Попробуйте снова.")
                    displayed_text = ""

        elif game_state == "battle":
            if not battle(hero, enemies, enemy_index):
                game_state = "game_over"
            else:
                enemy_index = (enemy_index + 1) % len(enemies)
                if enemy_index == 0:
                    game_state = "victory"
                save_game(hero, enemy_index, enemies)

        elif game_state == "victory":
            draw_victory()
            if displayed_text:
                if displayed_text == "Enter":  # You can customize the key press for restart
                    hero = None
                    enemy_index = 0
                    enemies = [
                        Enemy(13, 45, 4, 2, "Бандит", crit_chance=5),
                        Enemy(20, 60, 8, 5, "Паладин", crit_chance=10),
                        Enemy(18, 40, 2, 10, "Паук", crit_chance=20)
                    ]
                    game_state = "class_selection"
                    text_output.clear()
                    save_game(hero, enemy_index, enemies)
                else:
                    displayed_text = ""

        elif game_state == "game_over":
            screen.fill(BACKGROUND_COLOR)
            draw_text("Вы проиграли. Нажмите любую клавишу для выхода.", WIDTH // 2, HEIGHT // 2, RED, 36, center=True)
            pygame.display.flip()
            waiting_for_key = True
            while waiting_for_key:
                for event in pygame.event.get():
                    if event.type == pygame.KEYDOWN or event.type == pygame.QUIT:
                        save_game(hero, enemy_index, enemies)
                        pygame.quit()
                        sys.exit()

        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    main()
