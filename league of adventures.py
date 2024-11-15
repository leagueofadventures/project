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
    def __init__(self, dmg, hp, armor, money, dodge_chance, name):
        self.dmg = dmg
        self.original_dmg = dmg
        self.hp = hp
        self.original_hp = hp
        self.armor = armor
        self.money = money
        self.dodge_chance = dodge_chance
        self.name = name
        self.level = 1  # Начальный уровень
        self.exp = 0  # Текущий опыт
        self.next_level_exp = 100  # Опыт до следующего уровня

    def level_up(self):
        """Увеличиваем уровень, если набран достаточный опыт."""
        if self.exp >= self.next_level_exp:
            self.level += 1
            self.next_level_exp *= 2  # Каждый следующий уровень требует вдвое больше опыта
            self.exp = 0
            clrprint(f"{self.name} поднялся на уровень {self.level}!", Fore.GREEN)

    def gain_experience_and_gold(self, exp_gain, gold_gain):
        """Начисляем опыт и золото за победу."""
        self.exp += exp_gain
        self.money += gold_gain
        clrprint(f"{self.name} получил {exp_gain} опыта и {gold_gain} монет.", Fore.GREEN)
        self.level_up()

    def battle(self, enemy):
        while self.hp > 0 and enemy.hp > 0:
            # Расчёт урона героя
            body_part = random.choice(['head', 'body', 'body', 'body', 'leg', 'leg', 'leg', 'arm', 'arm', 'arm'])
            if body_part == 'head':
                hero_dmg = int(max(1, self.dmg * 2 - enemy.armor))
            elif body_part == 'body':
                hero_dmg = int(max(1, self.dmg - enemy.armor))
            elif body_part == 'leg':
                hero_dmg = int(max(1, self.dodge_chance - enemy.armor))
            elif body_part == 'arm':
                hero_dmg = int(max(1, self.dmg / 1.5 - enemy.armor))

            clrprint(f"{self.name} наносит {hero_dmg} урона в {body_part}.", Fore.GREEN)
            enemy.hp -= hero_dmg
            time.sleep(1)

            if enemy.hp <= 0:
                break

            # Расчёт урона врага
            krite = random.choice(['head'] + [1] * 9)
            if krite == 'head':
                enemy_dmg = max(1, enemy.dmg * 2 - self.armor)
                damage_message = f"КРИТ! {enemy.name} наносит {enemy_dmg} урона"
                clrprint(damage_message, Fore.RED)
            else:
                enemy_dmg = max(1, enemy.dmg - self.armor)
                clrprint(f"{enemy.name} наносит {enemy_dmg} урона", Fore.RED)

            # Проверяем, удалось ли герою уклониться от атаки
            if random.random() < self.dodge_chance:
                clrprint(f"{self.name} успешно уклонился!", Fore.GREEN)
            else:
                self.hp -= enemy_dmg
                
            time.sleep(1)

        # Проверка результата боя
        if self.hp > 0:
            clrprint("Вы победили!", Fore.YELLOW)
            self.gain_experience_and_gold(50, 5)  # За победу даём 50 опыта и 5 монет
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
    warrior = Hero(5, 40, 12, 15, 0, "Воин")  # Для воина шанс уклонения 0
    clrprint("Отличный выбор! Теперь ты – Воин", Fore.CYAN)
    print(f"Урон: {warrior.dmg}, здоровье: {warrior.hp}, броня: {warrior.armor}, монеты: {warrior.money}")
    
elif chosen_class == "маг":
    mage = Hero(20, 15, 0, 16, 0, "Маг")  # Маг теперь без шанса уклонения
    clrprint("Отличный выбор! Теперь ты – Маг", Fore.BLUE)
    print(f"Урон: {mage.dmg}, здоровье: {mage.hp}, броня: {mage.armor}, монеты: {mage.money}")
    
elif chosen_class == "плут":
    thief = Hero(15, 25, 7, 38, 0.05, "Плут")  # Плут теперь с шансом уклонения 5%
    clrprint("Отличный выбор! Теперь ты – Плут", Fore.GREEN)
    print(f"Урон: {thief.dmg}, здоровье: {thief.hp}, броня: {thief.armor}, монеты: {thief.money}")

# Создание врага
bandit = Enemy(13, 35, 4, "Бандит")

# Запуск боя
if chosen_class == "воин":
    warrior.battle(bandit)
elif chosen_class == "маг":
    mage.battle(bandit)
elif chosen_class == "плут":
    thief.battle(bandit)

input()
