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
SHOP_COLOR = (200, 200, 50)
SPELL_COLOR = (50, 200, 255)

# --- Создаем экран ---
screen = pygame.display.set_mode((WIDTH, HEIGHT))

input_text = ''

update_text = False

font = pygame.font.Font(None, 30)  # Adjusted font size for the input box

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
LIGHT_GRAY = (210, 210, 210)
DARK_GRAY = (169, 169, 169)

counter = 0

# --- Глобальные переменные для управления состоянием игры ---
STATE_MENU = 'menu'
STATE_BATTLE = 'battle'
STATE_SHOP = 'shop'
STATE_GAME_OVER = 'game_over'
STATE_VICTORY = 'victory'

current_state = STATE_MENU

# --- Класс текстового ввода --- (Остался без изменений) ---
class TextInputBox(pygame.sprite.Sprite):
    def __init__(self, x, y, width, font):
        super().__init__()
        self.color = BLACK
        self.backcolor = DARK_GRAY
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


text_input_box = TextInputBox(100, HEIGHT - 50, 600, font)  # Adjusted position for better visibility
group = pygame.sprite.Group(text_input_box)

# --- Функция для текста на экране ---
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
        self.spells = []  # Список заклинаний для Мага

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
                self.dmg = int(self.original_dmg + (self.original_dmg * increase_amount * 1))
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

    def cast_spell(self, spell, enemy):
        """
        Метод для применения заклинания.
        Возвращает сообщение о результате заклинания.
        """
        message = ""
        if spell['type'] == 'heal':
            heal_amount = spell['value']
            self.hp = min(self.original_hp, self.hp + heal_amount)
            message = f"{self.name} использовал заклинание 'Исцеление' и восстановил {heal_amount} HP!"
        elif spell['type'] == 'debuff':
            debuff_amount = spell['value']
            enemy.armor = max(0, enemy.armor - debuff_amount)
            message = f"{self.name} использовал заклинание 'Слабость' и снизил броню {enemy.name} на {debuff_amount}!"
        return message

# --- Класс Врага ---
class Enemy:
    def __init__(self, dmg, hp, armor, dodge_chance, name, crit_chance=10):
        self.name = name
        self.dmg = dmg
        self.hp = hp
        self.original_hp = hp
        self.armor = armor
        self.dodge_chance = dodge_chance
        self.crit_chance = crit_chance
        self.debuff_effect = 0  # Дополнительный дебафф, напр. снижение урона

    def attack(self, hero):
        is_crit = random.randint(1, 100) <= self.crit_chance
        damage = self.dmg * 2 if is_crit else self.dmg
        damage = int(max(1, (damage - hero.armor)))
        return damage, is_crit

# --- Функция магазина ---
def shop_menu(hero):
    global current_state
    shop_items = [
        {"name": "Улучшить урон (100 золота)", "type": "upgrade_dmg", "cost": 100},
        {"name": "Улучшить здоровье (150 золота)", "type": "upgrade_hp", "cost": 150},
        {"name": "Улучшить броню (120 золота)", "type": "upgrade_armor", "cost": 120},
    ]

    # Специальные заклинания для Мага
    if hero.name == "Маг":
        shop_items += [
            {"name": "Заклинание 'Исцеление' (200 золота)", "type": "spell_heal", "cost": 200, "spell": {"type": "heal", "value": 30}},
            {"name": "Заклинание 'Слабость' (250 золота)", "type": "spell_debuff", "cost": 250, "spell": {"type": "debuff", "value": 2}},
        ]

    selected = 0
    message = "Добро пожаловать в магазин!"
    while True:
        screen.fill(BACKGROUND_COLOR)
        draw_text("Магазин", WIDTH // 2, 50, SHOP_COLOR, size=50, center=True)
        draw_text(message, 10, 100, WHITE, size=24)

        for idx, item in enumerate(shop_items):
            color = WHITE
            if idx == selected:
                color = LIGHT_GRAY
            draw_text(f"{idx + 1}. {item['name']} - Цена: {item['cost']}", 50, 150 + idx * 40, color)

        draw_text("Используйте стрелки вверх/вниз для навигации и Enter для покупки.", 10, HEIGHT - 80, TEXT_COLOR, size=20)
        
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == KEYDOWN:
                if event.key == K_DOWN:
                    selected = (selected + 1) % len(shop_items)
                elif event.key == K_UP:
                    selected = (selected - 1) % len(shop_items)
                elif event.key == K_RETURN:
                    selected_item = shop_items[selected]
                    if hero.money >= selected_item['cost']:
                        hero.money -= selected_item['cost']
                        if selected_item['type'] == "upgrade_dmg":
                            hero.dmg += 2
                            message = "Урон увеличен на 2!"
                        elif selected_item['type'] == "upgrade_hp":
                            hero.original_hp += 20
                            hero.hp += 20
                            message = "Здоровье увеличено на 20!"
                        elif selected_item['type'] == "upgrade_armor":
                            hero.armor += 1
                            message = "Броня увеличена на 1!"
                        elif selected_item['type'] == "spell_heal":
                            if not any(spell['type'] == 'heal' for spell in hero.spells):
                                hero.spells.append(selected_item['spell'])
                                message = "Добавлено заклинание 'Исцеление'!"
                            else:
                                message = "У вас уже есть это заклинание."
                        elif selected_item['type'] == "spell_debuff":
                            if not any(spell['type'] == 'debuff' for spell in hero.spells):
                                hero.spells.append(selected_item['spell'])
                                message = "Добавлено заклинание 'Слабость'!"
                            else:
                                message = "У вас уже есть это заклинание."
                    else:
                        message = "Недостаточно золота!"
                    
        # Выход из магазина по нажатию ESC
        keys = pygame.key.get_pressed()
        if keys[K_ESCAPE]:
            current_state = STATE_BATTLE
            return

# --- Функция боя ---
def battle(hero, enemy):
    global current_state
    clock = pygame.time.Clock()
    running = True
    message = ""
    spell_message = ""
    spells_available = hero.spells if hero.name == "Маг" else []
    spell_selected = 0
    debuff_active = False
    enemy_original_armor = enemy.armor

    while running:
        screen.fill(BACKGROUND_COLOR)
        draw_text(f"{hero.name}: HP {hero.hp}/{hero.original_hp}, Уровень: {hero.level}, Деньги: {hero.money}, Опыт: {hero.exp}/{hero.next_level_exp}, Шанс уворота: {hero.dodge_chance}%", 10, 10, HERO_COLOR, size=24)
        draw_text(f"{enemy.name}: HP {enemy.hp}/{enemy.original_hp}", 10, 40, ENEMY_COLOR, size=24)
        draw_text(message, 10, 70, WHITE, size=24)
        draw_text(spell_message, 10, 100, SPELL_COLOR, size=24)

        # Для Мага отображаем доступные заклинания
        if spells_available:
            draw_text("Заклинания:", 10, 130, SPELL_COLOR, size=24)
            for idx, spell in enumerate(spells_available):
                spell_name = "Исцеление" if spell['type'] == 'heal' else "Слабость"
                draw_text(f"{idx + 1}. {spell_name}", 30, 160 + idx * 30, SPELL_COLOR, size=20)

            draw_text("Нажмите цифру от 1 до {0} для использования заклинания.".format(len(spells_available)), 10, 160 + len(spells_available)*30 + 10, SPELL_COLOR, size=20)

        pygame.display.flip()
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == KEYDOWN:
                if event.key == K_SPACE and not spells_available:
                    # Обычная атака
                    damage, part, is_hero_crit = hero.attack(enemy)
                    enemy.hp -= damage
                    crit_msg = "КРИТИЧЕСКИЙ УДАР! " if is_hero_crit else ""
                    message = f"{crit_msg}{hero.name} ударил по {part} на {damage} урона!"
                    if enemy.hp <= 0:
                        message = f"{enemy.name} повержен!"
                        hero.gain_experience_and_gold(50, 15)
                        hero.restore_health()
                        # После боя переходим в магазин
                        current_state = STATE_SHOP
                        return

                    # Враг атакует
                    if random.randint(1, 100) > hero.dodge_chance:
                        damage, is_enemy_crit = enemy.attack(hero)
                        hero.hp -= damage
                        crit_msg = "КРИТИЧЕСКИЙ УДАР! " if is_enemy_crit else ""
                        message += f" {crit_msg}{enemy.name} ответил на {damage} урона!"
                    else:
                        message += f" {hero.name} увернулся от атаки!"

                    if hero.hp <= 0:
                        message = "Вы проиграли. Игра окончена!"
                        current_state = STATE_GAME_OVER
                        return
                elif hero.name == "Маг":
                    # Использование заклинаний
                    if event.unicode.isdigit():
                        spell_idx = int(event.unicode) - 1
                        if 0 <= spell_idx < len(spells_available):
                            spell = spells_available[spell_idx]
                            spell_message = hero.cast_spell(spell, enemy)
                            # Применяем эффект заклинания
                            if spell['type'] == 'debuff':
                                debuff_active = True
                            elif spell['type'] == 'heal':
                                pass  # Heal уже применен
                            # Враг атакует после заклинания
                            if random.randint(1, 100) > hero.dodge_chance:
                                damage, is_enemy_crit = enemy.attack(hero)
                                hero.hp -= damage
                                crit_msg = "КРИТИЧЕСКИЙ УДАР! " if is_enemy_crit else ""
                                message = f"{crit_msg}{enemy.name} ответил на {damage} урона!"
                            else:
                                message = f"{hero.name} увернулся от атаки!"

                            if enemy.hp <= 0:
                                message = f"{enemy.name} повержен!"
                                hero.gain_experience_and_gold(50, 15)
                                hero.restore_health()
                                # После боя переходим в магазин
                                current_state = STATE_SHOP
                                return

                            if hero.hp <= 0:
                                message = "Вы проиграли. Игра окончена!"
                                current_state = STATE_GAME_OVER
                                return

        # Применение дебаффа (например, снижение брони врага)
        if debuff_active:
            enemy.armor = max(0, enemy.armor - 2)  # Снижаем броню на 2
            debuff_active = False
            message += f" Броня {enemy.name} снижена!"

# --- Функция для отображения состояния игры ---
def game_over_screen():
    global current_state
    while True:
        screen.fill(BACKGROUND_COLOR)
        draw_text("Вы проиграли!", WIDTH // 2, HEIGHT // 2 - 50, (255, 0, 0), size=50, center=True)
        draw_text("Нажмите ESC для выхода.", WIDTH // 2, HEIGHT // 2 + 10, WHITE, size=30, center=True)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    pygame.quit()
                    sys.exit()

def victory_screen():
    global current_state
    while True:
        screen.fill(BACKGROUND_COLOR)
        draw_text("Игра завершена. Победа!", WIDTH // 2, HEIGHT // 2 - 50, (0, 255, 0), size=50, center=True)
        draw_text("Нажмите ESC для выхода.", WIDTH // 2, HEIGHT // 2 + 10, WHITE, size=30, center=True)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    pygame.quit()
                    sys.exit()

# --- Главная программа ---
def main():
    global input_text, counter, current_state
    running = True
    clock = pygame.time.Clock()
    hero = None
    enemies = [
        Enemy(13, 45, 4, 2, "Бандит", crit_chance=5),
        Enemy(20, 60, 8, 5, "Паладин", crit_chance=10),
        Enemy(18, 40, 2, 10, "Паук", crit_chance=20)
    ]
    enemy_index = 0

    while running:
        screen.fill(BACKGROUND_COLOR)
        events = pygame.event.get()
        for event in events:
            if event.type == QUIT:
                running = False

        if current_state == STATE_MENU:
            # Экран выбора класса
            group.update(events)
            draw_text("Выберите класс: воин, маг, плут", WIDTH // 2, HEIGHT // 2 - 50, WHITE, size=40, center=True)
            group.draw(screen)
            if input_text.strip().lower() == 'воин':
                hero = Hero(7, 40, 12, 150, 20, "Воин")
                input_text = ''
                current_state = STATE_BATTLE
            elif input_text.strip().lower() == 'маг':
                hero = Hero(25, 15, 1, 160, 0, "Маг")
                input_text = ''
                current_state = STATE_BATTLE
            elif input_text.strip().lower() == 'плут':
                hero = Hero(15, 25, 7, 180, 5, "Плут")
                input_text = ''
                current_state = STATE_BATTLE

        elif current_state == STATE_BATTLE:
            if enemy_index < len(enemies):
                enemy = enemies[enemy_index]
                battle(hero, enemy)
                if hero.hp <= 0:
                    current_state = STATE_GAME_OVER
                else:
                    enemy_index += 1
            else:
                current_state = STATE_VICTORY

        elif current_state == STATE_SHOP:
            shop_menu(hero)
            current_state = STATE_BATTLE

        elif current_state == STATE_GAME_OVER:
            game_over_screen()

        elif current_state == STATE_VICTORY:
            victory_screen()

        pygame.display.flip()
        clock.tick(FPS)
        counter += 1

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
