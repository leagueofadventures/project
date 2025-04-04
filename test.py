import pygame
import sys
import json
import time
pygame.init()

size = 35
font_text = pygame.font.Font(None, size)

screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
pygame.display.set_caption('Gambit - Multiplayer')


# Цвета
white = (255, 255, 255)
black = (0, 0, 0)

def conclusion(rect_x, rect_y, width, height, x, y, color1, color2, text):
    rect = pygame.Rect(rect_x, rect_y, width, height)
    text_surface = font_text.render(text, True, color1, color2)
    text_rect = text_surface.get_rect()
    text_rect.topleft = (x, y)  
    pygame.draw.rect(screen, white, rect)
    screen.blit(text_surface, text_rect)
    return rect  # Возвращаем rect кнопки
    
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
        aa = '1'
        return aa
    

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

def load_menu():
    screen.fill(black)
    play_rect = conclusion(1100, 600, 300, 100, 1200, 630, black, white, 'Играть')
    pygame.display.flip()
    return play_rect

def show_load_menu():
    screen.fill(black)
    # Текст загрузки
    conclusion(850, 800, 300, 100, 1150, 630, white, black, 'Загрузить сохранение?')
    
    # Кнопка "нет"
    no_rect = conclusion(1400, 800, 300, 100, 950, 830, black, white, 'нет')
    
    # Кнопка "да"
    yes_rect = conclusion(1400, 800, 300, 100, 1500, 830, black, white, 'да')
    
    pygame.display.flip()
    
    # Возвращаем прямоугольники кнопок для обработки
    return no_rect, yes_rect

def showexcepterror():
    screen.fill(black)
    conclusion(1000, 600, 590, 100, 1020, 620, black, white, 'Сохранение не найдено. Начать новую игру?')
    no_rect2 = conclusion(1400, 950, 300, 100, 950, 1000, black, white, '1 - нет')
    yes_rect2 = conclusion(1400, 950, 300, 100, 1500, 1000, black, white, '2 - да')
    pygame.display.flip()
    return no_rect2, yes_rect2

run = True
show_menu = True
play_rect = load_menu()  # Сразу загружаем начальное меню и получаем rect кнопки
new_game = False
load_game_counter = False
show_error = False



while run:
    event_list = pygame.event.get()
    
    for event in event_list:
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            if play_rect.collidepoint(event.pos):
                no_rect, yes_rect = show_load_menu()
                load_game_counter = True
            
            if load_game_counter:
                    
                    # Проверяем нажатие на кнопки загрузки
                if no_rect.collidepoint(event.pos):
                    result = load_game()
                    if len(result) == 1:
                        no_rect2, yes_rect2 = showexcepterror()
                        show_error = True

            if show_error:
                if no_rect2.collidepoint(event.pos):
                    screen.fill(white)
            
                    
                
                    


                    

                
                

    

    pygame.display.flip()
