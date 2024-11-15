import random
import time
from random import randint
import time
from colorama import Fore, Back, Style
from colorama import init
init()

def clrprint(text, color=Fore.WHITE):
    print(color + text + Style.RESET_ALL)

class Hero:
    def __init__(self, dmg, hp, armor, money, name):
        self.dmg = dmg
        self.original_dmg = dmg
        self.hp = hp
        self.original_hp = hp
        self.armor = armor
        self.money = money
        self.name = name

    def battle(self, enemy):
        while self.hp > 0 and enemy.hp > 0:
            # Расчёт урона героя
            body_part = random.choice(['head', 'body', 'body', 'body', 'leg', 'leg', 'leg', 'arm', 'arm','arm'])
            if body_part == 'head':
                hero_dmg = int(max(0, self.dmg * 2 - enemy.armor))
            elif body_part == 'body':
                hero_dmg = int(max(0, self.dmg * 1.5 - enemy.armor))
            elif body_part == 'leg':
                hero_dmg = int(max(0, self.dmg - enemy.armor))
            elif body_part == 'arm':
                hero_dmg = int(max(0, self.dmg / 1.5 - enemy.armor))

            clrprint(f"{self.name} наносит {hero_dmg} урона в {body_part}.", Fore.GREEN)
            enemy.hp -= hero_dmg
            time.sleep(1)

            if enemy.hp <= 0:
                break

            # Расчёт урона врага
            enemy_dmg = max(1, enemy.dmg - self.armor)
            clrprint(f"{enemy.name} наносит {enemy_dmg} урона", Fore.RED)
            self.hp -= enemy_dmg
            time.sleep(1)

        if self.hp > 0:
            clrprint("Вы победили!", Fore.YELLOW)
            self.dmg = self.original_dmg
            self.hp = self.original_hp
        else:
            clrprint("Вы проиграли.", Fore.MAGENTA)


class Enemy:
    def __init__(self, dmg, hp, armor, name):
        self.name = name
        self.dmg = dmg
        self.hp = hp
        self.armor = armor
         

random_money = randint(1, 10)

# Выбор класса
while True:
    try:
        chosen_class = input("Выберите класс: воин, маг, плут\n").lower()
        if chosen_class in ["воин", "маг", "плут"]:
            break
        else:
            clrprint("Неверный ввод. Попробуйте снова.", Fore.RED)
    except KeyboardInterrupt:
        clrprint("\nПрограмму остановил пользователь.", Fore.RED)
        exit()

if chosen_class == "воин":
    warrior = Hero(10, 35, 10 + random_money, 15, "Воин")
    clrprint("Отличный выбор! Теперь ты – Воин", Fore.CYAN)
    print(f"Урон: {warrior.dmg}, здоровье: {warrior.hp}, броня: {warrior.armor}, монеты: {warrior.money}")
    
elif chosen_class == "маг":
    mage = Hero(22, 28, 6, 16, "Маг")
    clrprint("Отличный выбор! Теперь ты – Маг", Fore.BLUE)
    print(f"Урон: {mage.dmg}, здоровье: {mage.hp}, броня: {mage.armor}, монеты: {mage.money}")
    
elif chosen_class == "плут":
    thief = Hero(9, 24, 7, 38, "Плут")
    clrprint("Отличный выбор! Теперь ты – Плут", Fore.GREEN)
    print(f"Урон: {thief.dmg}, здоровье: {thief.hp}, броня: {thief.armor}, монеты: {thief.money}")

# Создание врага
bandit = Enemy(13, 30, 4, "Бандит")

# Запуск боя
if chosen_class == "воин":
    warrior.battle(bandit)
elif chosen_class == "маг":
    mage.battle(bandit)
elif chosen_class == "плут":
    thief.battle(bandit)


input()
