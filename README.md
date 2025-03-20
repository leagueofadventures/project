Хорошо, я объясню, как добавить функционал для сохранения просмотренных изображений в main.py. Поскольку у меня нет точного кода обработки изображений в вашем main.py, я предоставлю обобщенный подход, а вы сможете адаптировать его к своему конкретному коду.

Предположения:

У вас есть список или каталог изображений.
У вас есть механизм для показа изображений пользователю.
Вам необходимо отслеживать, какие изображения просматривал пользователь, и сохранять эту информацию между игровыми сеансами.
Шаги:

Инициализируйте список просмотренных изображений: в вашем main.py, создайте набор для хранения путей (или уникальных идентификаторов) просмотренных изображений. Используйте набор, потому что вы хотите, чтобы каждый элемент сохранялся только один раз.

# main.py
import pygame
import sys
from ui_elements import TextInputBox  # Import TextInputBox
from characters import Hero, Enemy
from battle import battle
from save_load import save_game, load_game
import os # Import the os module for file path manipulations

# Initialize Pygame, screen, etc.
pygame.init()
WIDTH, HEIGHT = pygame.display.Info().current_w, pygame.display.Info().current_h
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("RPG Битва")
font = pygame.font.Font(None, 30)

# Colors
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
LIGHT_GRAY = (200, 200, 200)
DARK_GRAY = (150, 150, 150)

# Game state variables
game_state = "class_selection"
input_text = ""
displayed_text = ""
update_text = False
text_output = []
counter = 0

# Create UI elements (TextInputBox)
input_box_y = HEIGHT - 100 if HEIGHT >= 1300 else HEIGHT - 100
text_input_box = TextInputBox(WIDTH//2 - 200, input_box_y, 400, font)
group = pygame.sprite.Group(text_input_box)

# Helper function for drawing text (if not already defined)
def draw_text(text, x, y, color=WHITE, size=30, center=False):
    font_render = pygame.font.Font(None, size)
    render = font_render.render(text, True, color)
    rect = render.get_rect()
    if center:
        rect.center = (x, y)
    else:
        rect.topleft = (x, y)
    screen.blit(render, rect)

# Function to create a Hero (if not already defined)
def create_hero(class_name):
    class_name = class_name.lower()
    if class_name == "воин":
        return Hero(10, 40, 5, 0, 0.02, "Воин")
    elif class_name == "маг":
        return Hero(20, 20, 2, 0, 0.05, "Маг")
    elif class_name == "плут":
        return Hero(15, 30, 3, 0, 0.30, "Плут")
    return None

def main():
    global game_state, input_text, displayed_text, update_text, counter, text_output

    hero, enemy_index, enemies = load_game()

    if enemies is None:
        enemies = [
            Enemy(10, 20, 6, 3, "Скелет", crit_chance=5),
            Enemy(15, 20, 6, 3, "Скелет", crit_chance=10),
            Enemy(20, 15, 7, 3, 'Скелет', crit_chance=15),
            Enemy(20, 45, 10, 10, "Главарь скелетов", crit_chance=20)
        ]

    if hero is None:
        game_state = "class_selection"
    else:
        game_state = "battle"

    # --- Image Handling ---
    image_dir = "images"  # Replace with your image directory
    all_image_paths = [os.path.join(image_dir, f) for f in os.listdir(image_dir) if f.endswith((".png", ".jpg", ".jpeg", ".gif"))]
    viewed_images = set()

    running = True
    while running:
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                save_game(hero, enemy_index, enemies)
                save_viewed_images(viewed_images)  # Save before quitting
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    save_game(hero, enemy_index, enemies)
                    save_viewed_images(viewed_images)  # Save before quitting
                    pygame.quit()
                    sys.exit()

        screen.fill(BLACK)  # Assuming BLACK is your background color

        if game_state == "class_selection":
            draw_text("Выберите класс: воин, маг, плут.", WIDTH//2, HEIGHT//2 - 100, WHITE, 48, center=True)
            update_text, displayed_text, input_text = text_input_box.update(events, update_text, displayed_text, input_text, counter)
            group.draw(screen)

            if displayed_text:
                hero = create_hero(displayed_text)
                if hero:
                    game_state = "battle"
                    displayed_text = ""
                    save_game(hero, enemy_index, enemies)
                else:
                    text_output.append("Некорректный выбор. Попробуйте снова.")  # Use text_output directly

        elif game_state == "battle":
            battle_result = battle(hero, enemies, enemy_index, text_output)  # Pass text_output
            if not battle_result:
                draw_text("Вы проиграли. Нажмите любую клавишу для выхода.", WIDTH // 2, HEIGHT // 2 + 100, RED, 36, center=True)
                pygame.display.flip()
                waiting_for_key = True
                while waiting_for_key:
                    for event in pygame.event.get():
                        if event.type == pygame.KEYDOWN or event.type == pygame.QUIT:
                            save_game(hero, enemy_index, enemies)
                            save_viewed_images(viewed_images)  # Save before quitting
                            pygame.quit()
                            sys.exit()
            else:
                enemy_index = (enemy_index + 1) % len(enemies)
                if enemy_index == 0:
                    game_state = "victory"
                save_game(hero, enemy_index, enemies)

        elif game_state == "victory":
            draw_text("Поздравляем! Вы победили всех врагов!", WIDTH // 2, HEIGHT // 2, GREEN, 48, center=True)
            pygame.display.flip() # Make sure victory text is visible
            pygame.time.wait(3000) # Show the message for 3 seconds

            # Reset the game
            hero = None
            enemy_index = 0
            enemies = [
                Enemy(10, 20, 6, 3, "Скелет", crit_chance=5),
                Enemy(15, 20, 6, 3, "Скелет", crit_chance=10),
                Enemy(20, 15, 7, 3, 'Скелет', crit_chance=15),
                Enemy(20, 45, 10, 10, "Главарь скелетов", crit_chance=20)
            ]
            game_state = "class_selection"
            text_output.clear()
            save_game(hero, enemy_index, enemies)

        pygame.display.flip()
        pygame.time.Clock().tick(60)

if __name__ == "__main__":
    main()
Загружать просмотренные изображения при запуске: измените mainфункцию для загрузки списка просмотренных изображений из файла при запуске игры.

# (Inside main.py, inside the main() function)

    # --- Image Handling ---
    image_dir = "images"  # Replace with your image directory
    all_image_paths = [os.path.join(image_dir, f) for f in os.listdir(image_dir) if f.endswith((".png", ".jpg", ".jpeg", ".gif"))]
    viewed_images = load_viewed_images() # Load viewed images from a file
Сохранение просмотренных изображений при выходе: измените основной цикл игры, чтобы сохранить список просмотренных изображений в файле при выходе из игры.

        for event in events:
            if event.type == pygame.QUIT:
                save_game(hero, enemy_index, enemies)
                save_viewed_images(viewed_images)  # Save before quitting
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    save_game(hero, enemy_index, enemies)
                    save_viewed_images(viewed_images)  # Save before quitting
                    pygame.quit()
                    sys.exit()
viewed_imagesВспомогательные функции: Создайте две новые функции для обработки загрузки и сохранения просмотренных изображений:

# save_load.py (recommended)
import json
import os

def save_game(hero, enemy_index, enemies):
    # ... (save_game function) ...
    pass

def load_game():
    # ... (load_game function) ...
    pass

def save_viewed_images(viewed_images, filename="viewed_images.json"):
    """Saves the set of viewed image paths to a JSON file."""
    try:
        with open(filename, "w") as f:
            json.dump(list(viewed_images), f)  # Convert set to list for JSON serialization
    except Exception as e:
        print(f"Error saving viewed images: {e}")

def load_viewed_images(filename="viewed_images.json"):
    """Loads the set of viewed image paths from a JSON file."""
    try:
        with open(filename, "r") as f:
            image_list = json.load(f)
            return set(image_list)  # Convert back to a set
    except FileNotFoundError:
        return set()  # Return an empty set if the file doesn't exist
    except Exception as e:
        print(f"Error loading viewed images: {e}")
        return set()

# characters.py
class Hero:
    # ... (Hero class definition) ...
    pass

class Enemy:
    # ... (Enemy class definition) ...
    pass
Отметить изображения как просмотренные: когда изображение отображается пользователю, добавьте его путь (или идентификатор) в viewed_imagesнабор.

    # Assuming you have a function to show an image
    def show_image(image_path):
        image = pygame.image.load(image_path)
        screen.blit(image, (0, 0)) # example
        pygame.display.flip()

        # Mark the image as viewed:
        viewed_images.add(image_path) # Add the *path*
Полный переработанный фрагмент:


# main.py
import pygame
import sys
from ui_elements import TextInputBox  # Import TextInputBox
from characters import Hero, Enemy
from battle import battle
from save_load import save_game, load_game, save_viewed_images, load_viewed_images
import os # Import the os module for file path manipulations

# Initialize Pygame, screen, etc.
pygame.init()
WIDTH, HEIGHT = pygame.display.Info().current_w, pygame.display.Info().current_h
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("RPG Битва")
font = pygame.font.Font(None, 30)

# Colors
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
LIGHT_GRAY = (200, 200, 200)
DARK_GRAY = (150, 150, 150)

# Game state variables
game_state = "class_selection"
input_text = ""
displayed_text = ""
update_text = False
text_output = []
counter = 0

# Create UI elements (TextInputBox)
input_box_y = HEIGHT - 100 if HEIGHT >= 1300 else HEIGHT - 100
text_input_box = TextInputBox(WIDTH//2 - 200, input_box_y, 400, font)
group = pygame.sprite.Group(text_input_box)

# Helper function for drawing text (if not already defined)
def draw_text(text, x, y, color=WHITE, size=30, center=False):
    font_render = pygame.font.Font(None, size)
    render = font_render.render(text, True, color)
    rect = render.get_rect()
    if center:
        rect.center = (x, y)
    else:
        rect.topleft = (x, y)
    screen.blit(render, rect)

# Function to create a Hero (if not already defined)
def create_hero(class_name):
    class_name = class_name.lower()
    if class_name == "воин":
        return Hero(10, 40, 5, 0, 0.02, "Воин")
    elif class_name == "маг":
        return Hero(20, 20, 2, 0, 0.05, "Маг")
    elif class_name == "плут":
        return Hero(15, 30, 3, 0, 0.30, "Плут")
    return None

def show_image(screen, image_path, viewed_images):
    """Display an image on the screen and mark it as viewed."""
    try:
        image = pygame.image.load(image_path)
        screen.blit(image, (0, 0))  # Adjust coordinates as needed
        pygame.display.flip()
        viewed_images.add(image_path)
    except pygame.error as e:
        print(f"Error loading or displaying image: {e}")

def main():
    global game_state, input_text, displayed_text, update_text, counter, text_output

    hero, enemy_index, enemies = load_game()

    if enemies is None:
        enemies = [
            Enemy(10, 20, 6, 3, "Скелет", crit_chance=5),
            Enemy(15, 20, 6, 3, "Скелет", crit_chance=10),
            Enemy(20, 15, 7, 3, 'Скелет', crit_chance=15),
            Enemy(20, 45, 10, 10, "Главарь скелетов", crit_chance=20)
        ]

    if hero is None:
        game_state = "class_selection"
    else:
        game_state = "battle"

    # --- Image Handling ---
    image_dir = "images"  # Replace with your image directory
    all_image_paths = [os.path.join(image_dir, f) for f in os.listdir(image_dir) if f.endswith((".png", ".jpg", ".jpeg", ".gif"))]
    viewed_images = load_viewed_images() # Load viewed images from a file

    running = True
    while running:
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                save_game(hero, enemy_index, enemies)
                save_viewed_images(viewed_images)  # Save before quitting
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    save_game(hero, enemy_index, enemies)
                    save_viewed_images(viewed_images)  # Save before quitting
                    pygame.quit()
                    sys.exit()

        screen.fill(BLACK)  # Assuming BLACK is your background color

        if game_state == "class_selection":
            draw_text("Выберите класс: воин, маг, плут.", WIDTH//2, HEIGHT//2 - 100, WHITE, 48, center=True)
            update_text, displayed_text, input_text = text_input_box.update(events, update_text, displayed_text, input_text, counter)
            group.draw(screen)

            if displayed_text:
                hero = create_hero(displayed_text)
                if hero:
                    game_state = "battle"
                    displayed_text = ""
                    save_game(hero, enemy_index, enemies)
                else:
                    text_output.append("Некорректный выбор. Попробуйте снова.")  # Use text_output directly

        elif game_state == "battle":
            battle_result = battle(hero, enemies, enemy_index, text_output)  # Pass text_output
            if not battle_result:
                draw_text("Вы проиграли. Нажмите любую клавишу для выхода.", WIDTH // 2, HEIGHT // 2 + 100, RED, 36, center=True)
                pygame.display.flip()
                waiting_for_key = True
                while waiting_for_key:
                    for event in pygame.event.get():
                        if event.type == pygame.KEYDOWN or event.type == pygame.QUIT:
                            save_game(hero, enemy_index, enemies)
                            save_viewed_images(viewed_images)  # Save before quitting
                            pygame.quit()
                            sys.exit()
            else:
                enemy_index = (enemy_index + 1) % len(enemies)
                if enemy_index == 0:
                    game_state = "victory"
                save_game(hero, enemy_index, enemies)

        elif game_state == "victory":
            draw_text("Поздравляем! Вы победили всех врагов!", WIDTH // 2, HEIGHT // 2, GREEN, 48, center=True)
            pygame.display.flip() # Make sure victory text is visible
            pygame.time.wait(3000) # Show the message for 3 seconds

            # Reset the game
            hero = None
            enemy_index = 0
            enemies = [
                Enemy(10, 20, 6, 3, "Скелет", crit_chance=5),
                Enemy(15, 20, 6, 3, "Скелет", crit_chance=10),
                Enemy(20, 15, 7, 3, 'Скелет', crit_chance=15),
                Enemy(20, 45, 10, 10, "Главарь скелетов", crit_chance=20)
            ]
            game_state = "class_selection"
            text_output.clear()
            save_game(hero, enemy_index, enemies)

        pygame.display.flip()
        pygame.time.Clock().tick(60)

# Outside of the main() function

if __name__ == "__main__":
    main()
Важные соображения:

Уникальность пути изображения: Убедитесь, что пути к изображениям, которые вы используете, уникальны. Если вы генерируете изображения динамически, вам может понадобиться другой способ их идентификации.
Обработка ошибок: добавьте обработку ошибок в save_viewed_imagesфункции load_viewed_imagesи для корректной обработки потенциальных ошибок ввода-вывода файлов.
Расположение файла: Подумайте, где вы хотите сохранить viewed_images.jsonфайл (например, в каталоге данных игры). Используйте os.path.joinдля создания путей, независимых от платформы.
Формат данных: JSON — простой формат, но если у вас очень большое количество изображений, вы можете рассмотреть более эффективный метод хранения (например, базу данных).
Интеграция игровой логики: адаптируйте код, чтобы он идеально вписывался в логику вашей игры для отображения изображений.
Такой подход позволит вашей игре запомнить, какие изображения игрок видел между сеансами. Не забудьте скорректировать код в соответствии со спецификой вашего проекта.
