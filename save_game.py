import random
import time
from colorama import Fore, Style, init
import json
import os

init()

SAVE_FILE = "savegame.json"

def clrprint(text, color=Fore.WHITE):
    print(color + text + Style.RESET_ALL)

# Класс героя
class Hero:
    def __init__(self, dmg, hp, armor, money, dodge_chance, name, level=1, exp=0, next_level_exp=100, hero_class="Воин"):
        self.dmg = dmg
        self.original_dmg = dmg
        self.hp = hp
        self.original_hp = hp
        self.armor = armor
        self.money = money
        self.dodge_chance = dodge_chance
        self.name = name
        self.level = level
        self.exp = exp
        self.next_level_exp = next_level_exp
        self.hero_class = hero_class
        self.abilities = []  # Список способностей героя
        self.cooldowns = {}  # Словарь для отслеживания кулдаунов способностей

    def level_up(self):
        if self.exp >= self.next_level_exp:
            self.level += 1
            self.next_level_exp = int(self.next_level_exp * 1.5) # Уменьшил рост необходимого опыта для следующего уровня
            self.exp = 0
            clrprint(f"{self.name} поднялся на уровень {self.level}!", Fore.GREEN)

            # Увеличение характеристик
            increase_amount = self.level * 0.15 #Уменьшил прирост хар-к
            self.dmg = int(self.original_dmg + (self.original_dmg * increase_amount))
            self.original_dmg = self.dmg
            self.hp = int(self.original_hp + (self.original_hp * increase_amount))
            self.original_hp = self.hp
            self.armor = int(self.armor + (self.armor * increase_amount))
            self.dodge_chance += 0.005 # Увеличил прирост уклонения

            clrprint("Характеристики после повышения уровня:", Fore.YELLOW)
            clrprint(f"  Уровень: {self.level}", Fore.YELLOW)
            clrprint(f"  Урон: {self.dmg}", Fore.YELLOW)
            clrprint(f"  Здоровье: {self.hp}", Fore.YELLOW)
            clrprint(f"  Броня: {self.armor}", Fore.YELLOW)
            clrprint(f"  Шанс уклонения: {self.dodge_chance:.2%}", Fore.YELLOW)

    def gain_experience_and_gold(self, exp_gain, gold_gain):
        self.exp += exp_gain
        self.money += gold_gain
        clrprint(f"{self.name} получил {exp_gain} опыта и {gold_gain} монет.", Fore.GREEN)
        self.level_up()

    def restore_health(self):
        self.hp = self.original_hp
        clrprint(f"{self.name} восстановил своё здоровье до {self.hp}", Fore.GREEN)

    def add_ability(self, ability):
        """Добавляет способность герою."""
        self.abilities.append(ability)
        self.cooldowns[ability.name] = 0  # Инициализация кулдауна

    def use_ability(self, ability_name, target):
        """Использует способность героя."""
        for ability in self.abilities:
            if ability.name == ability_name:
                if self.cooldowns[ability_name] <= 0:
                    ability.use(self, target)
                    self.cooldowns[ability_name] = ability.cooldown
                else:
                    clrprint(f"Способность '{ability_name}' на кулдауне! Осталось: {self.cooldowns[ability_name]} ходов.", Fore.RED)
                return
        clrprint(f"Способность '{ability_name}' не найдена!", Fore.RED)

    def battle(self, enemy):
        while self.hp > 0 and enemy.hp > 0:
            # Ход героя
            clrprint(f"\nХод {self.name}:", Fore.GREEN)
            clrprint(f"{self.name}: {self.hp} HP", Fore.GREEN)
            clrprint(f"{enemy.name}: {enemy.hp} HP", Fore.RED)
            clrprint(f"1. Атаковать", Fore.CYAN)
            clrprint(f"2. Использовать способность", Fore.CYAN)
            choice = input("Выберите действие (1/2): ")
            if choice == "1":
                body_part = random.choice(['head', 'body', 'body', 'body', 'leg', 'leg', 'leg', 'arm', 'arm', 'arm'])
                hero_dmg = max(1, self.dmg - enemy.armor)
                if body_part == 'head':
                    hero_dmg = int(hero_dmg * 2)
                elif body_part == 'leg':
                    hero_dmg = int(hero_dmg / 1.2)
                elif body_part == 'arm':
                    hero_dmg = int(hero_dmg / 1.5)

                clrprint(f"{self.name} наносит {hero_dmg} урона в {body_part} противнику {enemy.name}.", Fore.GREEN)
                enemy.hp -= hero_dmg
                time.sleep(1)
            elif choice == "2":
                if not self.abilities:
                    clrprint("У вас нет доступных способностей!", Fore.RED)
                else:
                    clrprint("Доступные способности:", Fore.CYAN)
                    for i, ability in enumerate(self.abilities, 1):
                        cooldown = self.cooldowns[ability.name]
                        clrprint(f"{i}. {ability.name} (Кулдаун: {cooldown} ходов)", Fore.YELLOW)
                    ability_choice = input("Выберите номер способности: ")
                    if ability_choice.isdigit() and 1 <= int(ability_choice) <= len(self.abilities):
                        ability_index = int(ability_choice) - 1
                        self.use_ability(self.abilities[ability_index].name, enemy)
                    else:
                        clrprint("Неверный выбор способности!", Fore.RED)
                        continue
            else:
                clrprint("Неверный выбор действия!", Fore.RED)
                continue

            if enemy.hp <= 0:
                break

            # Ход врага
            clrprint(f"\nХод {enemy.name}:", Fore.RED)
            enemy.battle_turn(self)

            # Уменьшение кулдаунов способностей
            for ability_name in self.cooldowns:
                if self.cooldowns[ability_name] > 0:
                    self.cooldowns[ability_name] -= 1

        if self.hp > 0:
            clrprint(f"Вы победили {enemy.name}!", Fore.YELLOW)
            self.gain_experience_and_gold(enemy.exp_reward, enemy.gold_reward) # Добавил награды за победу
            self.restore_health()
            return True
        else:
            clrprint("Вы проиграли. Прогресс сброшен.", Fore.RED)
            reset_progress()
            return False

# Класс врага
class Enemy:
    def __init__(self, dmg, hp, armor, dodge_chance, name, abilities=None, exp_reward = 50, gold_reward = 10):
        self.name = name
        self.dmg = dmg
        self.hp = hp
        self.original_hp = hp
        self.armor = armor
        self.dodge_chance = dodge_chance
        self.abilities = abilities or []  # Список способностей врага
        self.cooldowns = {ability.name: 0 for ability in self.abilities}  # Словарь для отслеживания кулдаунов способностей
        self.exp_reward = exp_reward
        self.gold_reward = gold_reward

    def use_ability(self, ability_name, target):
        """Использует способность врага."""
        for ability in self.abilities:
            if ability.name == ability_name:
                if self.cooldowns[ability_name] <= 0:
                    ability.use(self, target)
                    self.cooldowns[ability_name] = ability.cooldown
                else:
                    clrprint(f"{self.name} не может использовать '{ability_name}' из-за кулдауна!", Fore.RED)
                return
        clrprint(f"Способность '{ability_name}' не найдена у {self.name}!", Fore.RED)

    def battle_turn(self, target):
        """Ход врага в бою."""
        time.sleep(1)
        if self.abilities and random.random() < 0.3:  # 30% шанс использовать способность
            ability = random.choice(self.abilities)
            self.use_ability(ability.name, target)
        else:
            enemy_dmg = max(1, self.dmg - target.armor)
            if random.random() < target.dodge_chance:
                clrprint(f"{target.name} уклонился от удара {self.name}!", Fore.GREEN)
            else:
                clrprint(f"{self.name} наносит {enemy_dmg} урона {target.name}.", Fore.RED)
                target.hp -= enemy_dmg
            time.sleep(1)

        # Уменьшение кулдаунов способностей
        for ability_name in self.cooldowns:
            if self.cooldowns[ability_name] > 0:
                self.cooldowns[ability_name] -= 1

# Класс способности
class Ability:
    def __init__(self, name, description, effect, cooldown):
        self.name = name
        self.description = description
        self.effect = effect
        self.cooldown = cooldown

    def use(self, user, target):
        clrprint(f"{user.name} использует способность '{self.name}': {self.description}", Fore.YELLOW)
        self.effect(user, target)

# Примеры способностей для героя
def heal_ability(user, target):
    heal_amount = int(user.original_hp * 0.3)  # Восстанавливает 30% от максимального здоровья
    user.hp = min(user.original_hp, user.hp + heal_amount)
    clrprint(f"{user.name} восстановил {heal_amount} здоровья.", Fore.GREEN)

def power_strike_ability(user, target):
    damage = int(user.dmg * 1.5)  # Урон увеличивается на 50%
    target.hp -= max(1, damage - target.armor)
    clrprint(f"{user.name} наносит мощный удар, нанося {damage} урона {target.name}!", Fore.RED)

def shield_ability(user, target):
    user.armor += int(user.armor*0.3) #Изменил механику работы щита
    clrprint(f"{user.name} активирует щит, увеличивая броню на 30%.", Fore.CYAN)

# Примеры способностей для врагов
def poison_strike_ability(user, target):
    damage = int(user.dmg * 0.5)  # Наносит 50% от урона
    target.hp -= max(1, damage - target.armor)
    clrprint(f"{user.name} наносит ядовитый удар, нанося {damage} урона {target.name}!", Fore.RED)
    # Применение яда (например, урон в следующем ходу)
    def poison_effect(target):
        poison_dmg = int(user.dmg * 0.2)  # 20% от урона врага
        if target.hp > 0:
            target.hp -= max(1, poison_dmg)
            clrprint(f"{target.name} теряет {poison_dmg} здоровья из-за яда!", Fore.RED)
    target.poison_effect = lambda: poison_effect(target) # Добавил вызов функции

def taunt_ability(user, target):
    target.dodge_chance = max(0, target.dodge_chance - 0.05)  # Уменьшает шанс уклонения на 5%
    clrprint(f"{user.name} провоцирует {target.name}, снижая его шанс уклонения на 5%!", Fore.YELLOW)

def regenerate_ability(user, target): # Добавил регенерацию
        heal_amount = int(user.original_hp * 0.2)
        user.hp = min(user.original_hp, user.hp + heal_amount)
        clrprint(f"{user.name} восстанавливает {heal_amount} здоровья.", Fore.GREEN)

def reduce_armor_ability(user, target):
    target.armor = max(0, target.armor - 5)
    clrprint(f"{user.name} снижает броню {target.name} на 5 ед.", Fore.RED)

enemies = [
    Enemy(10, 30, 2, 0, "Бандит", abilities=[
        Ability("Удар кинжалом", "Быстрый удар кинжалом", lambda u, t: t.hp -= max(1, u.dmg - t.armor), 2)
    ], exp_reward=35, gold_reward=8),
    Enemy(13, 35, 2, 0.1, "Огр", abilities=[
        Ability("Мощный удар", "Мощный удар дубиной", lambda u, t: power_strike_ability(u, t), 3)  # Исправлено: добавлена лямбда-функция
    ], exp_reward=45, gold_reward=12),
    Enemy(17, 40, 5, 0.03, "Гигантский волк", abilities=[
        Ability("Ядовитый укус", "Укус с ядовитым эффектом", lambda u, t: poison_strike_ability(u, t), 4)  # Исправлено: добавлена лямбда-функция
    ], exp_reward=60, gold_reward=15),
    Enemy(15, 65, 10, 0.05, "Дракон", abilities=[
        Ability("Огненное дыхание", "Огненное дыхание, наносящее урон", lambda u, t: t.hp -= max(1, u.dmg * 2 - t.armor), 5)
    ], exp_reward=150, gold_reward=50),
    Enemy(12, 45, 7, 0.07, "Колдун", abilities=[
        Ability("Проклятие", "Снижает шанс уклонения противника", lambda u, t: taunt_ability(u, t), 3)  # Исправлено: добавлена лямбда-функция
    ], exp_reward=70, gold_reward=20),
    Enemy(20, 50, 15, 0.1, "Тролль", abilities=[
        Ability("Регенерация", "Восстанавливает здоровье", lambda u, t: regenerate_ability(u, t), 4)  # Исправлено: добавлена лямбда-функция
    ], exp_reward=80, gold_reward=25),
    Enemy(18, 70, 8, 0.08, "Медведь", abilities=[
        Ability("Сокрушительный удар", "Мощный удар лапой", lambda u, t: power_strike_ability(u, t), 3)  # Исправлено: добавлена лямбда-функция
    ], exp_reward=90, gold_reward=30),
    Enemy(25, 80, 20, 0.12, "Гигант", abilities=[
        Ability("Топот", "Снижает броню противника", lambda u, t: reduce_armor_ability(u, t), 5)  # Исправлено: добавлена лямбда-функция
    ], exp_reward=180, gold_reward=60),
]
# Функция выбора класса героя
def choose_hero_class():
    hero_classes = {
        "1": {"name": "Воин", "dmg": 7, "hp": 40, "armor": 12, "money": 15, "dodge_chance": 0.05},
        "2": {"name": "Маг", "dmg": 15, "hp": 30, "armor": 5, "money": 15, "dodge_chance": 0.1},
        "3": {"name": "Разбойник", "dmg": 11, "hp": 35, "armor": 7, "money": 35, "dodge_chance": 0.15}
    }
    clrprint("Выберите класс героя:", Fore.CYAN)
    for key, cls in hero_classes.items():
        clrprint(f"{key}. {cls['name']}", Fore.YELLOW)
        clrprint(f"   Урон: {cls['dmg']}, Здоровье: {cls['hp']}, Броня: {cls['armor']}, Шанс уклонения: {cls['dodge_chance'] * 100}%", Fore.WHITE)
    while True:
        choice = input("Введите номер класса: ")
        if choice in hero_classes:
            cls = hero_classes[choice]
            name = input("Введите имя героя: ")
            clrprint(f"Вы выбрали класс: {cls['name']}", Fore.GREEN)
            return Hero(cls['dmg'], cls['hp'], cls['armor'], cls['money'], cls['dodge_chance'], name, hero_class=cls['name'])
        else:
            clrprint("Неверный выбор, попробуйте снова.", Fore.RED)

# Функция сохранения игры
def save_game(hero, enemies):
    save_data = {
        "hero": {
            "dmg": hero.original_dmg, # Сохраняем оригинальный урон
            "hp": hero.original_hp, # Сохраняем оригинальное здоровье
            "armor": hero.armor,
            "money": hero.money,
            "dodge_chance": hero.dodge_chance,
            "name": hero.name,
            "level": hero.level,
            "exp": hero.exp,
            "next_level_exp": hero.next_level_exp,
            "hero_class": hero.hero_class,
            "abilities": [ability.name for ability in hero.abilities],  # Сохранение названий способностей
            "cooldowns": hero.cooldowns,  # Сохранение кулдаунов
        },
        "enemies": [
            {
                "name": enemy.name,
                "dmg": enemy.dmg,
                "hp": enemy.original_hp,
                "armor": enemy.armor,
                "dodge_chance": enemy.dodge_chance,
                "abilities": [ability.name for ability in enemy.abilities],
                "exp_reward": enemy.exp_reward,
                "gold_reward": enemy.gold_reward
            }
            for enemy in enemies
        ]
    }

    try:
        with open(SAVE_FILE, "w") as f:
            json.dump(save_data, f)
        clrprint("Игра сохранена!", Fore.GREEN)
    except Exception as e:
        clrprint(f"Ошибка при сохранении игры: {e}", Fore.RED)

# Функция загрузки игры
def load_game():
    try:
        with open(SAVE_FILE, "r") as f:
            save_data = json.load(f)
        hero_data = save_data["hero"]

        hero = Hero(
            hero_data["dmg"],
            hero_data["hp"],
            hero_data["armor"],
            hero_data["money"],
            hero_data["dodge_chance"],
            hero_data["name"],
            hero_data["level"],
            hero_data["exp"],
            hero_data["next_level_exp"],
            hero_data["hero_class"]
        )
        hero.cooldowns = hero_data["cooldowns"]
        # Восстановление способностей героя
        for ability_name in hero_data["abilities"]:
            if ability_name == "Мощный удар":
                hero.add_ability(Ability("Мощный удар", "Увеличивает урон на 50%", power_strike_ability, 3))
            elif ability_name == "Щит":
                hero.add_ability(Ability("Щит", "Увеличивает броню", shield_ability, 4))
            elif ability_name == "Лечение":
                hero.add_ability(Ability("Лечение", "Восстанавливает 30% здоровья", heal_ability, 3))
            elif ability_name == "Огненный шар":
                hero.add_ability(Ability("Огненный шар", "Наносит двойной урон", lambda u, t: t.hp -= max(1, u.dmg * 2 - t.armor), 4))
            elif ability_name == "Скрытность":
                hero.add_ability(Ability("Скрытность", "Увеличивает шанс уклонения на 10%", lambda u, t: u.dodge_chance += 0.1, 3))
            elif ability_name == "Отравленный удар":
                hero.add_ability(Ability("Отравленный удар", "Наносит ядовитый урон", poison_strike_ability, 4))
        # Восстановление врагов
        loaded_enemies = []
        for enemy_data in save_data["enemies"]:
            abilities = []
            for ability_name in enemy_data["abilities"]:
                if ability_name == "Удар кинжалом":
                    abilities.append(Ability("Удар кинжалом", "Быстрый удар кинжалом", lambda u, t: t.hp -= max(1, u.dmg - t.armor), 2))
                elif ability_name == "Мощный удар":
                    abilities.append(Ability("Мощный удар", "Мощный удар дубиной", power_strike_ability, 3))
                elif ability_name == "Ядовитый укус":
                    abilities.append(Ability("Ядовитый укус", "Укус с ядовитым эффектом", poison_strike_ability, 4))
                elif ability_name == "Огненное дыхание":
                    abilities.append(Ability("Огненное дыхание", "Огненное дыхание, наносящее урон", lambda u, t: t.hp -= max(1, u.dmg * 2 - t.armor), 5))
                elif ability_name == "Проклятие":
                    abilities.append(Ability("Проклятие", "Снижает шанс уклонения противника", taunt_ability, 3))
                elif ability_name == "Регенерация":
                    abilities.append(Ability("Регенерация", "Восстанавливает здоровье", regenerate_ability, 4))
                elif ability_name == "Сокрушительный удар":
                    abilities.append(Ability("Сокрушительный удар", "Мощный удар лапой", power_strike_ability, 3))
                elif ability_name == "Топот":
                    abilities.append(Ability("Топот", "Снижает броню противника", reduce_armor_ability, 5))

            enemy = Enemy(
                enemy_data["dmg"],
                enemy_data["hp"],
                enemy_data["armor"],
                enemy_data["dodge_chance"],
                enemy_data["name"],
                abilities,
                enemy_data["exp_reward"],
                enemy_data["gold_reward"]
            )
            loaded_enemies.append(enemy)

        clrprint("Игра загружена!", Fore.GREEN)
        return hero, loaded_enemies

    except FileNotFoundError:
        clrprint("Сохраненная игра не найдена.", Fore.RED)
        return None, None
    except Exception as e:
        clrprint(f"Ошибка при загрузке игры: {e}", Fore.RED)
        return None, None

# Функция сброса прогресса
def reset_progress():
    try:
        os.remove(SAVE_FILE)
        clrprint("Прогресс сброшен.", Fore.YELLOW)
    except FileNotFoundError:
        clrprint("Сохраненная игра не найдена.", Fore.RED)
    except Exception as e:
        clrprint(f"Ошибка при сбросе прогресса: {e}", Fore.RED)

# Функция магазина
def shop(hero):
    while True:
        clrprint("\nМагазин:", Fore.CYAN)
        clrprint(f"Ваше золото: {hero.money}", Fore.YELLOW)
        clrprint("1. Купить зелье здоровья (+30% HP) - 50 золота", Fore.GREEN)
        clrprint("2. Улучшить броню (+5) - 30 золота", Fore.GREEN)
        clrprint("3. Улучшить урон (+3) - 40 золота", Fore.GREEN)
        clrprint("4. Выйти из магазина", Fore.MAGENTA)

        choice = input("Выберите действие: ")
        if choice == "1":
            if hero.money >= 50:
                hero.money -= 50
                hero.hp = min(hero.original_hp, hero.hp + int(hero.original_hp * 0.3)) # Добавлние зелья
                clrprint(f"{hero.name} купил зелье здоровья и восстановил здоровье до {hero.hp}.", Fore.GREEN)
            else:
                clrprint("Недостаточно золота!", Fore.RED)
        elif choice == "2":
            if hero.money >= 30:
                hero.money -= 30
                hero.armor += 5
                clrprint(f"{hero.name} улучшил броню. Броня: {hero.armor}", Fore.GREEN)
            else:
                clrprint("Недостаточно золота!", Fore.RED)
        elif choice == "3":
            if hero.money >= 40:
                hero.money -= 40
                hero.dmg += 3
                hero.original_dmg += 3
                clrprint(f"{hero.name} улучшил урон. Урон: {hero.dmg}", Fore.GREEN)
            else:
                clrprint("Недостаточно золота!", Fore.RED)
        elif choice == "4":
            break
        else:
            clrprint("Неверный выбор действия. Попробуйте снова.", Fore.RED)

# Начало игры
current_hero, enemies = load_game()
if not current_hero or not enemies:
    clrprint("Начало новой игры!", Fore.CYAN)
    current_hero = choose_hero_class()  # Выбор класса героя
    enemies = [
        Enemy(10, 30, 2, 0, "Бандит", abilities=[
            Ability("Удар кинжалом", "Быстрый удар кинжалом", lambda u, t: t.hp -= max(1, u.dmg - t.armor), 2)
        ], exp_reward=35, gold_reward=8),
        Enemy(13, 35, 2, 0.1, "Огр", abilities=[
            Ability("Мощный удар", "Мощный удар дубиной", power_strike_ability, 3)
        ], exp_reward=45, gold_reward=12),
        Enemy(17, 40, 5, 0.03, "Гигантский волк", abilities=[
            Ability("Ядовитый укус", "Укус с ядовитым эффектом", poison_strike_ability, 4)
        ], exp_reward=60, gold_reward=15),
        Enemy(15, 65, 10, 0.05, "Дракон", abilities=[
            Ability("Огненное дыхание", "Огненное дыхание, наносящее урон", lambda u, t: t.hp -= max(1, u.dmg * 2 - t.armor), 5)
        ], exp_reward=150, gold_reward=50),
        Enemy(12, 45, 7, 0.07, "Колдун", abilities=[
            Ability("Проклятие", "Снижает шанс уклонения противника", taunt_ability, 3)
        ], exp_reward=70, gold_reward=20),
        Enemy(20, 50, 15, 0.1, "Тролль", abilities=[
            Ability("Регенерация", "Восстанавливает здоровье", regenerate_ability, 4)
        ], exp_reward=80, gold_reward=25),
        Enemy(18, 70, 8, 0.08, "Медведь", abilities=[
            Ability("Сокрушительный удар", "Мощный удар лапой", power_strike_ability, 3)
        ], exp_reward=90, gold_reward=30),
        Enemy(25, 80, 20, 0.12, "Гигант", abilities=[
            Ability("Топот", "Снижает броню противника", reduce_armor_ability, 5)
        ], exp_reward=180, gold_reward=60),
    ]

# Добавление способностей герою в зависимости от класса
if current_hero.hero_class == "Воин":
    current_hero.add_ability(Ability("Мощный удар", "Увеличивает урон на 50%", power_strike_ability, 3))
    current_hero.add_ability(Ability("Щит", "Увеличивает броню на 30%", shield_ability, 4))
elif current_hero.hero_class == "Маг":
    current_hero.add_ability(Ability("Лечение", "Восстанавливает 30% здоровья", heal_ability, 3))
    current_hero.add_ability(Ability("Огненный шар", "Наносит двойной урон", lambda u, t: t.hp -= max(1, u.dmg * 2 - t.armor), 4))
elif current_hero.hero_class == "Разбойник":
    current_hero.add_ability(Ability("Скрытность", "Увеличивает шанс уклонения на 10%", lambda u, t: u.dodge_chance += 0.1, 3))
    current_hero.add_ability(Ability("Отравленный удар", "Наносит ядовитый урон", poison_strike_ability, 4))

# Игровой цикл
game_is_running = True
while game_is_running:
    # Применение эффектов от способностей, например, яда
    if hasattr(current_hero, "poison_effect") and current_hero.hp > 0:
        current_hero.poison_effect()
        if current_hero.hp <= 0:
            clrprint(f"{current_hero.name} погиб от яда!", Fore.RED)
            reset_progress()
            game_is_running = False
            break
    clrprint("\nВыберите действие:", Fore.CYAN)
    clrprint(f"Герой: {current_hero.name}, Уровень: {current_hero.level}, Опыт: {current_hero.exp}/{current_hero.next_level_exp}, Золото: {current_hero.money}", Fore.CYAN)
    clrprint("1. Посетить магазин", Fore.YELLOW)
    clrprint("2. Сразиться с врагом", Fore.RED)
    clrprint("3. Сохранить игру", Fore.GREEN)
    clrprint("4. Выйти из игры", Fore.MAGENTA)

    choice = input("Введите номер действия: ")
    if choice == "1":
        shop(current_hero)
    elif choice == "2":
        if not enemies:
            clrprint("Вы победили всех врагов! Игра завершена.", Fore.GREEN)
            game_is_running = False
        else:
            enemy = random.choice(enemies)
            clrprint(f"Вы встретили {enemy.name}!", Fore.RED)
            if current_hero.battle(enemy):
                enemies.remove(enemy)
                save_game(current_hero, enemies)
            else:
                game_is_running = False
    elif choice == "3":
        save_game(current_hero, enemies)
    elif choice == "4":
        clrprint("Выход из игры. Спасибо за игру!", Fore.MAGENTA)
        game_is_running = False
    else:
        clrprint("Неверный выбор действия. Попробуйте снова.", Fore.RED)

clrprint("Спасибо за игру!", Fore.CYAN)
input("Нажмите Enter, чтобы выйти...")
