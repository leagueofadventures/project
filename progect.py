import os
import pygame
import sys
import time
from moviepy import VideoFileClip
from colorama import init, Fore, Style
from resize import resize
import fight2

# Initialize Pygame
pygame.init()
pygame.mixer.init()

# Set up screen
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
screen_width, screen_height = screen.get_size()

# Define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
LIGHT_GRAY = (210, 210, 210)
DARK_GRAY = (169, 169, 169)

# Global variables
input_text = ""
displayed_text = ""
viewed_images = []  # List to store viewed images
viewed_images_file = "viewed_images.txt"  # File to save viewed images

# Load viewed images from file
def load_viewed_images():
    if os.path.exists(viewed_images_file):
        with open(viewed_images_file, 'r') as f:
            return [line.strip() for line in f.readlines()]
    return []

# Save viewed images to file
def save_viewed_images():
    with open(viewed_images_file, 'w') as f:
        for image_path in viewed_images:
            f.write(image_path + '\n')

# Load viewed images at the start
viewed_images = load_viewed_images()

# Your existing code...
input_text = ""
displayed_text = ""  # Variable to store text to be displayed on the screen

# Счетчик для обновления
counter = 0

# Флаг для обновления текста
update_text = False

# Класс для инпут бокса
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
        pygame.draw.rect(self.image, self.color if self.active else DARK_GRAY, self.image.get_rect().inflate(-2, -2), 2)
        if self.active and self.cursor_visible:
            cursor_y = 5 + (len(lines) - 1) * self.font.get_height()
            cursor_x = 5 + self.font.size(current_line)[0]
            pygame.draw.rect(self.image, self.color, (cursor_x, cursor_y, 2, self.font.get_height()))
        self.rect = self.image.get_rect(topleft=self.pos)

    def update(self, events):
        global update_text, input_text, displayed_text  # Declare variables as global
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.rect.collidepoint(event.pos):
                    self.active = True
                else:
                    self.active = False
            if event.type == pygame.KEYDOWN and self.active:
                if event.key == pygame.K_RETURN:
                    input_text = self.text  # Store the entered text
                    displayed_text = input_text  # Update the displayed text
                    self.active = False
                    self.text = ""
                    self.render_text()
                    update_text = True  # Set the flag to update text
                elif event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                    self.render_text()
                elif event.key == pygame.K_DELETE:
                    self.text = ""
                    self.render_text()
                else:
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

        if update_text and self.active:
            self.render_text()
            update_text = False  # Reset the flag here

        if counter % 20 == 0:  # Changed update frequency for better visual
            self.backcolor = LIGHT_GRAY if counter % 40 == 0 else DARK_GRAY
            self.render_text()

        current_time = pygame.time.get_ticks()
        if current_time - self.cursor_timer > 500:
            self.cursor_visible = not self.cursor_visible
            self.cursor_timer = current_time
            self.render_text()


# Параметры текста в инпут
font = pygame.font.SysFont(None, 32)  # Размер шрифта уменьшен для примера
clock = pygame.time.Clock()
text_input_box = TextInputBox(1800, 1250, 400, font)  # Координаты внутри экрана
group = pygame.sprite.Group(text_input_box)

resize("1.png")
resize('Settings.png')
resize('menu.jpg')
resize('2.png')
resize('1.blur.png')
resize('3.png')
resize('3.blur.png')
resize('2.blur.png')
resize('4.png')
resize('4.blur.png')
resize('5.jpg')
resize('5.blur.jpg')
resize('6.jpg')
resize('6.blur.jpg')
resize('7.jpg')
resize('7.blur.png')
resize('8.jpg')
resize('8.blur.png')
resize('9.jpg')
resize('10.jpg')
resize('11.jpg')
print(Style.RESET_ALL)

void = fight2.Hero(10, 10, 10, 10, 10, 'gg')

enemy = fight2.Enemy(10, 10, 10, 10, 'gg')

# Загрузка изображений и аудио
images = ['1.png', '2.png', '3.png', '4.png', '5.jpg', '6.jpg', '7.jpg', '8.jpg', '9.jpg', '10.jpg', '11.png']
image_surfaces = {}

for image in images:
    try:
        image_surfaces[image] = pygame.image.load(image).convert()
    except pygame.error as e:
        print(f"Не удалось загрузить изображение {image}: {e}")

try:
    settings_image = pygame.image.load('Settings.png').convert()  # Исправлена лишняя скобка and added .convert()

    menu_image = pygame.image.load('menu.jpg').convert()
    
    pygame.mixer.music.load('12.mp3')
    
except pygame.error as e:
    image = None
    print(f"Не удалось загрузить одно из изображений: {e}")

# Загрузка видеофайла
try:
    clip = VideoFileClip('video.mp4')
    video_width, video_height = clip.size
    duration = clip.duration
    current_frame_time = 0
except IOError as e:
    clip = None
    print(f"Не удалось загрузить видеофайл: {e}")

# Параметры текста
font_text = pygame.font.Font(None, 50)
font_text1 = pygame.font.Font(None, 35)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (66, 170, 255)

# Создание текстовых поверхностей
text_surface1 = font_text.render('Однажды в одном мире зародилась жизнь', True, BLACK)
text_rect1 = text_surface1.get_rect()
text_rect1.topleft = (10, 1300)  # Пример координат




text_surface_menu_play = font_text1.render('Чтобы играть, нажмите 1', True, BLACK, WHITE)
text_rect_menu_play = text_surface_menu_play.get_rect()
text_rect_menu_play.centerx = screen_width // 2
text_rect_menu_play.centery = screen_height // 2 - 50

text_surface_menu_settings = font_text1.render('Чтобы зайти в настройки,', True, BLACK, WHITE)
text_rect_menu_settings = text_surface_menu_settings.get_rect()
text_rect_menu_settings.centerx = screen_width // 2
text_rect_menu_settings.centery = screen_height // 2 + 50

text_surface_menu_settings_2 = font_text1.render('нажмите 2', True, BLACK, WHITE)
text_rect_menu_settings_2 = text_surface_menu_settings_2.get_rect()
text_rect_menu_settings_2.centerx = screen_width // 2
text_rect_menu_settings_2.centery = screen_height // 2 + 90



text_surface_pause = font_text1.render('Продолжить - 5', True, BLACK)
text_rect_pause = text_surface_pause.get_rect()
text_rect_pause.centerx = screen_width // 2
text_rect_pause.centery = screen_height // 2 - 50

text_surface_pause_settings = font_text1.render('настройки - 4', True, BLACK, WHITE)
text_rect_pause_settings = text_surface_pause_settings.get_rect()
text_rect_pause_settings.centerx = screen_width // 2
text_rect_pause_settings.centery = screen_height // 2 + 50





# Установка прозрачности (alpha). 128 — это значение для полупрозрачности (50%).
alpha = 128

# Создание поверхностей (functions for semi-transparent squares)
square_surface = pygame.Surface((400, 150), pygame.SRCALPHA)
square_surface1 = pygame.Surface((400, 150), pygame.SRCALPHA)
square_surface2 = pygame.Surface((400, 150), pygame.SRCALPHA)
square_surface3 = pygame.Surface((400, 150), pygame.SRCALPHA)

# Заполнение поверхностей полупрозрачным цветом (например, белым)
square_surface.fill((255, 255, 255, alpha))
square_surface1.fill((255, 255, 255, alpha))
square_surface2.fill((255, 255, 255, alpha))
square_surface3.fill((255, 255, 255, alpha))

def make_frame(t):
    if clip:
        try:
            frame = clip.get_frame(t)
            # Преобразование кадра видео в изображение Pygame
            surf = pygame.surfarray.make_surface(frame.swapaxes(0, 1))
            return surf
        except Exception as e:
            print(f"Error getting video frame at time {t}: {e}")
            return None
    return None

# Инициализация флагов и переменных
running = True
show_text = 0
show_settings = 0
show_input = 0
show_video = 0
show_menu = 1
show_firstimage = 0
music = 0
show_image = 0
show_game_settings = 0
paused = False

blur1 = 0

blur2 = 0

blur3 = 0

image_flag = 0
pygame.mixer.music.play(-1) # Play music indefinitely

# Find the last viewed image index
if viewed_images:
    last_viewed_image = viewed_images[-1]
    current_image = images.index(last_viewed_image)
else:
    current_image = 0

# In the main loop, when displaying an image, add it to the viewed_images list
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if show_menu:
                if event.key == pygame.K_1:
                    show_menu = 0
                    show_firstimage = 1
                if event.key == pygame.K_2:
                    show_menu = 0
                    show_settings = 1
            elif show_settings:
                if event.key == pygame.K_ESCAPE:
                    show_settings = 0
                    show_firstimage = 1
            elif show_firstimage:
                if event.key == pygame.K_ESCAPE:
                    show_firstimage = 0
                    show_menu = 1
                if event.key == pygame.K_RIGHT or event.key == pygame.K_SPACE:
                    show_firstimage = 0
                    show_image = 1
                    if images[current_image] not in viewed_images:
                        viewed_images.append(images[current_image])  # Add to viewed images
                        save_viewed_images()  # Save viewed images to file
            elif show_image:
                if event.key == pygame.K_ESCAPE:
                    show_image = 0
                    show_firstimage = 1
                if event.key == pygame.K_RIGHT or event.key == pygame.K_SPACE:
                    current_image += 1
                    if current_image >= len(images):
                        current_image = 0
                    if images[current_image] not in viewed_images:
                        viewed_images.append(images[current_image])  # Add to viewed images
                        save_viewed_images()  # Save viewed images to file
            elif show_video:
                if event.key == pygame.K_SPACE:
                    paused = not paused
                if event.key == pygame.K_ESCAPE:
                    show_video = 0
                    show_menu = 1
        group.update([event])

    screen.fill(BLACK) # Fill the screen with black each frame

    if show_menu and menu_image:
        screen.blit(menu_image, (0, 0))
        screen.blit(square_surface, (screen_width // 2 - 200, screen_height // 2 - 125))
        screen.blit(square_surface1, (screen_width // 2 - 200, screen_height // 2 - 25))
        screen.blit(text_surface_menu_play, text_rect_menu_play)
        screen.blit(text_surface_menu_settings, text_rect_menu_settings)
        screen.blit(text_surface_menu_settings_2, text_rect_menu_settings_2)
    elif show_settings and settings_image:
        screen.blit(settings_image, (0, 0))
        # Add settings rendering logic here
    elif show_firstimage and image_surfaces[images[current_image]]:
        screen.blit(image_surfaces[images[current_image]], (0, 0))
    elif show_image:
        screen.blit(image_surfaces[images[current_image]], (0, 0))
    elif show_video:
        if clip:
            if not paused:
                current_frame_time += clock.tick(60) / 1000.0
                if current_frame_time >= duration:
                    current_frame_time = 0  # Loop video
            frame = make_frame(current_frame_time)
            if frame is not None:
                # Scale the frame to fit the screen while maintaining aspect ratio
                frame_ratio = frame.get_width() / frame.get_height()
                screen_ratio = screen_width / screen_height
                if frame_ratio > screen_ratio:
                    new_width = screen_width
                    new_height = int(new_width / frame_ratio)
                else:
                    new_height = screen_height
                    new_width = int(new_height * frame_ratio)
                frame = pygame.transform.scale(frame, (new_width, new_height))
                screen.blit(frame, ((screen_width - new_width) // 2, (screen_height - new_height) // 2))

    if show_input:
        group.draw(screen)
        if displayed_text:
            text_surface = font.render(displayed_text, True, WHITE)
            screen.blit(text_surface, (10, screen_height - text_surface.get_height() - 10))

    if show_text:
        screen.blit(text_surface1, text_rect1)

    pygame.display.flip()
    clock.tick(60)
    counter += 1

# At the end of the main loop, save viewed images
save_viewed_images()

# Clean up
pygame.quit()
sys.exit()
