import pygame
import random
import time
from random import randint
from colorama import Fore, Back, Style
from colorama import init
import json

pygame.init()
screen = pygame.display.set_mode((600, 400))
font = pygame.font.Font(None, 36)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    

    screen.fill((0, 0, 0))  # Clear the screen (black)

    pygame.display.flip()





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

    def text(self):
        text_surface_level_up = font.render(f"{self.name} поднялся на уровень {self.level}!", True, (255, 255, 255))
        text_surface12 = font.render("Характеристики после повышения уровня:", True, (255, 255, 255))
        text_surface_up_level = font.render(f"Уровень: {self.level}", True, (255, 255, 255))
        text_surface_up_dmg = font.render(f"  Урон: {self.dmg}", True, (255, 255, 255))
        text_surface_up_hp = font.render(f"  Здоровье: {self.hp}", True, (255, 255, 255))
        text_surface_up_armor = font.render(f"  Броня: {self.armor}", True, (255, 255, 255))
        text_surface_up_dodge = font.render(f"  Шанс уклонения: {self.dodge_chance:.2%}", True, (255, 255, 255))

        text_surface_get_xp = font.render(f"{self.name} получил {exp_gain} опыта и {gold_gain} монет.", True, (255, 255, 255))

        text_surface_hill = font.render(f"{self.name} восстановил своё здоровье до {self.hp}", True, (255, 255, 255))

        text_surface_dmg = font.render(f"{self.name} наносит {hero_dmg} урона в {body_part}.", True, (255, 255, 255))

        text_surface_enemy_dmg = font.render(f"{enemy.name} наносит {enemy_dmg} урона", True, (255, 255, 255))
    

    def level_up(self):
        if self.exp >= self.next_level_exp:
            self.level += 1
            self.next_level_exp *= 2
            self.exp = 0
            screen.blit(text_surface_level_up, (100, 100))

            # Увеличение характеристик при повышении уровня
            increase_amount = self.level * 0.2
            self.dmg = int(self.original_dmg + (self.original_dmg * increase_amount))
            self.original_dmg = self.dmg
            self.hp = int(self.original_hp + (self.original_hp * increase_amount))
            self.original_hp = self.hp
            self.armor = int(self.armor + (self.armor * increase_amount))
            self.dodge_chance += 0.001

            screen.blit(text_surface, (100, 100))
            screen.blit(text_surface, (100, 100))
            screen.blit(text_surface3, (100, 100))
            screen.blit(text_surface15, (100, 100))
            screen.blit(text_surface_up_armor, (100, 100))
            screen.blit(text_surface_up_dodge, (100, 100))

    def gain_experience_and_gold(self, exp_gain, gold_gain):
        self.exp += exp_gain
        self.money += gold_gain
        screen.blit(text_surface_get_xp, (0, 0))
        self.level_up()

    def restore_health(self):
        self.hp = self.original_hp
        screen.blit(text_surface_hill, (0, 0))

    def battle(self, enemy):
        while self.hp > 0 and enemy.hp > 0:
            body_part = random.choice(['head', 'body', 'body', 'leg', 'leg', 'leg', 'leg', 'arm', 'arm', 'arm', 'arm'])
            if body_part == 'head':
                hero_dmg = int(max(1, self.dmg * 2 - enemy.armor))
            elif body_part == 'body':
                hero_dmg = int(max(1, self.dmg - enemy.armor))
            elif body_part == 'leg':
                hero_dmg = int(max(1, self.dmg / 1.2 - enemy.armor))
            elif body_part == 'arm':
                hero_dmg = int(max(1, self.dmg / 1.5 - enemy.armor))

            screen.blit(text_surface_dmg, (0, 0))
            enemy.hp -= hero_dmg
            time.sleep(1)

            if enemy.hp <= 0:
                break

            krite = random.choice(['head', 'body', 'body', 'body', 'body', 'body', 'body', 'body', 'body', 'body', 'body'])
            if krite == 'head':
                enemy_dmg = max(1, enemy.dmg * 2 - self.armor)
                damage_message = f"КРИТ! {enemy.name} наносит {enemy_dmg} урона"
                text_surface_damage_message = font.render(damage_message, True, (255, 255, 255))
                screen.blit(text_surface_dmg_message, (0, 0))
      
            else:
                enemy_dmg = max(1, enemy.dmg - self.armor)
                screen.blit(text_surface_enemy_dmg, (0, 0))

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

pygame.quit()
