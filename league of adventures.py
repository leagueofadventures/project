import random
import time
from random import randint
from colorama import Fore, Back, Style
from colorama import init
import json

init()

def clrprint(text, color=Fore.WHITE):
    print(color + text + Style.RESET_ALL)

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
            clrprint(f"{self.name} поднялся на уровень {self.level}!", Fore.GREEN)

            # Увеличение характеристик при повышении уровня
            increase_amount = self.level * 0.2
            self.dmg = int(self.original_dmg + (self.original_dmg * increase_amount))
            self.original_dmg = self.dmg
            self.hp = int(self.original_hp + (self.original_hp * increase_amount))
            self.original_hp = self.hp
            self.armor = int(self.armor + (self.armor * increase_amount))
            self.dodge_chance += 0.001

            clrprint("Характеристики после повышения уровня:", Fore.YELLOW)
            clrprint(f"  Уровень: {self.level}", Fore.YELLOW)
            clrprint(f"  Урон: {self.dmg}", Fore.YELLOW)
            clrprint(f"  Здоровье: {self.hp}", Fore.YELLOW)
            clrprint(f"  Броня: {self.armor}", Fore.YELLOW)
            clrprint(f"  Шанс уклонения: {self.dodge_chance:.2%}", Fore.YELLOW)  # Форматирование в процентах

    def gain_experience_and_gold(self, exp_gain, gold_gain):
        self.exp += exp_gain
        self.money += gold_gain
        clrprint(f"{self.name} получил {exp_gain} опыта и {gold_gain} монет.", Fore.GREEN)
        self.level_up()

    def restore_health(self):
        self.hp = self.original_hp
        clrprint(f"{self.name} восстановил своё здоровье до {self.hp}", Fore.GREEN)

    def battle(self, enemy):
        while self.hp > 0 and enemy.hp > 0:
            body_part = random.choice(['head', 'body', 'body', 'body', 'leg', 'leg', 'leg', 'arm', 'arm', 'arm'])
            if body_part == 'head':
                hero_dmg = int(max(1, self.dmg * 2 - enemy.armor))
            elif body_part == 'body':
                hero_dmg = int(max(1, self.dmg - enemy.armor))
            elif body_part == 'leg':
                hero_dmg = int(max(1, self.dmg / 1.2 - enemy.armor))
            elif body_part == 'arm':
                hero_dmg = int(max(1, self.dmg / 1.5 - enemy.armor))

            clrprint(f"{self.name} наносит {hero_dmg} урона в {body_part}.", Fore.GREEN)
            enemy.hp -= hero_dmg
            time.sleep(1)

            if enemy.hp <= 0:
                break

            krite = random.choice(['head', 'body', 'body', 'body', 'body', 'body', 'body', 'body', 'body', 'body', 'body'])
            if krite == 'head':
                enemy_dmg = max(1, enemy.dmg * 2 - self.armor)
                damage_message = f"КРИТ! {enemy.name} наносит {enemy_dmg} урона"
                clrprint(damage_message, Fore.RED)
            else:
                enemy_dmg = max(1, enemy.dmg - self.armor)
                clrprint(f"{enemy.name} наносит {enemy_dmg} урона", Fore.RED)

            if random.random() < self.dodge_chance:
                clrprint(f"{self.name} успешно уклонился!", Fore.GREEN)
            else:
                self.hp -= enemy_dmg

            time.sleep(1)

        if self.hp > 0:
            clrprint("Вы победили!", Fore.YELLOW)
            self.gain_experience_and_gold(50, 5)
            self.restore_health()
            return True
        else:
            clrprint("Вы проиграли.", Fore.MAGENTA)
            clrprint("Игра окончена.", Fore.RED)
            return False

class Enemy:
    def __init__(self, dmg, hp, armor, dodge_chance, name):
        self.name = name
        self.dmg = dmg
        self.hp = hp
        self.armor = armor
        self.dodge_chance = dodge_chance

while True:
    try:
        chosen_class = input("Выберите класс: воин, маг, плут\n").lower()
        if chosen_class in ["воин", "маг", "плут", '201106']:
            break
        else:
            clrprint("Неверный ввод. Попробуйте снова.", Fore.RED)
    except KeyboardInterrupt:
        clrprint("\nПрограмму остановил пользователь.", Fore.RED)
        exit()

if chosen_class == "воин":
    current_hero = Hero(7, 40, 12, 15, 0, "Воин")
    clrprint("Отличный выбор! Теперь ты – Воин", Fore.CYAN)
    print(f"Урон: {current_hero.dmg}, здоровье: {current_hero.hp}, броня: {current_hero.armor}, монеты: {current_hero.money}")

elif chosen_class == "маг":
    current_hero = Hero(25, 15, 1, 16, 0, "Маг")
    clrprint("Отличный выбор! Теперь ты – Маг", Fore.BLUE)
    print(f"Урон: {current_hero.dmg}, здоровье: {current_hero.hp}, броня: {current_hero.armor}, монеты: {current_hero.money}")

elif chosen_class == "плут":
    current_hero = Hero(15, 25, 7, 38, 0.05, "Плут")
    clrprint("Отличный выбор! Теперь ты – Плут", Fore.GREEN)
    print(f"Урон: {current_hero.dmg}, здоровье: {current_hero.hp}, броня: {current_hero.armor}, монеты: {current_hero.money}")
elif chosen_class == "201106":
    current_hero = Hero(9999999999, 9999999999, 999999999, 3999999, 0.05, "АДМИН")
    clrprint("Отличный выбор! Теперь ты – АДМИН", Fore.RED)
    print(f"Урон: {current_hero.dmg}, здоровье: {current_hero.hp}, броня: {current_hero.armor}, монеты: {current_hero.money}")

bandit = Enemy(13, 35, 4, 0, "Бандит")
paladin = Enemy(14, 30, 0, 5, 'Паладин')
pavuk = Enemy(15, 35, 4, 5, 'Паук')
pavuk2 = Enemy(15, 35, 4, 5, 'Паук')
pavuk3 = Enemy(12, 30, 4, 10, 'Паук')
pavuk4 = Enemy(10, 40, 6, 1, 'Паук')
pavuk5 = Enemy(16, 60, 8, 30, 'Паук')

enemies = [bandit, paladin, pavuk, pavuk2, pavuk3, pavuk4, pavuk5]

game_is_running = True
for enemy in enemies:
    if game_is_running:
        game_is_running = current_hero.battle(enemy)
        time.sleep(5)
    else:
        break

input()
