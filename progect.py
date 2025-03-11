import pygame
from pygame.locals import *
import sys
import time
from moviepy.editor import VideoFileClip

pygame.init()
pygame.mixer.init()

# Установите разрешение экрана по необходимости. Здесь используется полный экран.
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
screen_width, screen_height = screen.get_size()

# Define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
LIGHT_GRAY = (210, 210, 210)
DARK_GRAY = (169, 169, 169)

# Global variables to store input text and update flag
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



# Параметры текста в инпут
font = pygame.font.SysFont(None, 32)  # Размер шрифта уменьшен для примера
clock = pygame.time.Clock()
text_input_box = TextInputBox(1800, 1250, 400, font)  # Координаты внутри экрана
group = pygame.sprite.Group(text_input_box)

# Загрузка изображений и аудио
try:
    image = pygame.image.load("1.png")
    
    settings_image = pygame.image.load('Settings.png')
    
    menu_image = pygame.image.load('menu.jpg')
    
    second_image = pygame.image.load('2.png') 
    
    pygame.mixer.music.load('12.mp3')
    
    image_blur = pygame.image.load('1.blur.png')
    
    third_image = pygame.image.load('3.png')
    
    third_image_blur = pygame.image.load('3.blur.png')
    
    second_image_blur = pygame.image.load('2.blur.png')
    
    fourth_image = pygame.image.load('4.png')

    fourth_image_blur = pygame.image.load('4.blur.png')

    fifth_image = pygame.image.load('5.jpg')

    fifth_image_blur = pygame.image.load('5.blur.jpg')

    sixth_image = pygame.image.load('6.jpg')

    sixth_image_blur = pygame.image.load('6.blur.jpg')

    seventh_image = pygame.image.load('7.jpg')

    seventh_image_blur = pygame.image.load('7.blur.png')


    eighth_image = pygame.image.load('8.jpg')

    eighth_image_blur = pygame.image.load('8.blur.png')
    
except pygame.error:
    image = None
    print("Не удалось загрузить одно из изображений.")

# Загрузка видеофайла
clip = VideoFileClip('video.mp4')
video_width, video_height = clip.size
duration = clip.duration

# Получение rect для изображений
settings_image_rect = settings_image.get_rect()
third_image_blur_rect = third_image_blur.get_rect()
third_image_rect = third_image.get_rect()
image_rect = image.get_rect()
second_image_rect = second_image.get_rect()
menu_image_rect = menu_image.get_rect()
image_blur_rect = image_blur.get_rect()
second_image_blur_rect = second_image_blur.get_rect()


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
text_rect_menu_play.topleft = (1150, 550)  # Пример координат

text_surface_menu_settings = font_text1.render('Чтобы зайти в настройки,', True, BLACK, WHITE)
text_rect_menu_settings = text_surface_menu_settings.get_rect()
text_rect_menu_settings.topleft = (1150, 750)  # Пример координат

text_surface_menu_settings_2 = font_text1.render('нажмите 2', True, BLACK, WHITE)
text_rect_menu_settings_2 = text_surface_menu_settings_2.get_rect()
text_rect_menu_settings_2.topleft = (1230, 790)  # Пример координат



text_surface2 = font_text.render('В ней появились разные существа. Одни были злые другие добрые а некоторые вообще не относились ни к первым ни к другим.', True, BLACK)
text_rect2 = text_surface2.get_rect()
text_rect2.topleft = (10, 1300)  # Пример координат

text_surface3 = font_text.render('Они могли помогать нежити и уничтожать добрых. Но и наоборот.', True, BLACK)
text_rect3 = text_surface3.get_rect()
text_rect3.topleft = (10, 1350)  # Пример координат

text_surface4 = font_text.render('В ней поселились очень добрые жители и они делились между собой чем угодно. Но их деревня была в зоне королевства.', True, BLACK)
text_rect4 = text_surface3.get_rect()
text_rect4.topleft = (10, 1350)  # Пример координат

text_surface_pause = font_text1.render('Продолжить - 5', True, BLACK)
text_rect_pause = text_surface_pause.get_rect()
text_rect_pause.topleft = (1170, 550)  # Пример координат

text_surface_pause_settings = font_text1.render('настройки - 4', True, BLACK, WHITE)
text_rect_pause_settings = text_surface_pause_settings.get_rect()
text_rect_pause_settings.topleft = (1170, 750)  # Пример координат

text_surface4 = font_text.render('В этом мире зародилась цивилизация и в некоторых местах появились некие постройки.', True, BLACK)
text_rect4 = text_surface4.get_rect()
text_rect4.topleft = (10, 1300)  # Пример координат

text_surface5 = font_text.render('Среди этих построек и зародилась одна особенная деревня.', True, BLACK)
text_rect5 = text_surface5.get_rect()
text_rect5.topleft = (10, 1350)  # Пример координат


text_surface6 = font_text.render('В ней поселились очень добрые жители и они делились между собой чем угодно.', True, BLACK)
text_rect6 = text_surface6.get_rect()
text_rect6.topleft = (10, 1310)  # Пример координат


text_surface7 = font_text.render('В этой деревне было много вкусной еды.', True, BLACK)
text_rect7 = text_surface7.get_rect()
text_rect7.topleft = (10, 1310)  # Пример координат


text_surface8 = font_text.render('Среди этих построек и зародилась одна особенная деревня.', True, BLACK)
text_rect8 = text_surface8.get_rect()
text_rect8.topleft = (10, 1310)  # Пример координат


text_surface9 = font_text.render('Но их деревня была в зоне королевства.', True, BLACK)
text_rect9 = text_surface9.get_rect()
text_rect9.topleft = (10, 1310)  # Пример координат


text_surface10 = font_text.render('Это дало повод королю отнять у ник большую часть продовольствия. Ведь король очень любил брать чужое счастье себе.', True, BLACK)
text_rect10 = text_surface10.get_rect()
text_rect10.topleft = (10, 1310)  # Пример координат



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
    frame = clip.get_frame(t)
    # Преобразование кадра видео в изображение Pygame
    surf = pygame.surfarray.make_surface(frame.swapaxes(0, 1))
    return surf

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

blur1 = 0

blur2 = 0

blur3 = 0

image_flag = 0

space = False

# Список изображений и соответствующих текстов
images = [
    (image, text_surface1, text_rect1),
    (second_image, text_surface2, text_rect2),
    (text_surface3, text_rect3),
    (third_image, text_surface4, text_rect4),
    (text_surface5, text_rect5),
    (fourth_image, text_surface6, text_rect6),
    (fifth_image, text_surface7, text_rect7),
    (sixth_image, text_surface8, text_rect8),
    (seventh_image, text_surface9, text_rect9),
    (eighth_image, text_surface10, text_rect10),
]

image_index = 0  # Индекс текущего отображаемого изображения
image_timer = pygame.time.get_ticks()  # Время последнего обновления изображения
image_delay = 5000  # Задержка между сменой изображений (в миллисекундах)


# Основной цикл
screen.fill(WHITE)
while running:
    event_list = pygame.event.get()
    for event in event_list:
        if event.type == QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and image_flag == 1:
                if show_game_settings == 1:
                    pass
                else:
                    show_image += 1

            elif event.key == pygame.K_1:
                show_video = 1
                show_menu = 0

            elif event.key == pygame.K_2:
                show_settings = 1
                if show_menu == 0:
                    show_settings = 2
                    show_menu = 1

            elif event.key == pygame.K_4 and show_game_settings == 1:
                show_game_settings = 2

            elif event.key == pygame.K_3:
                music += 1
                pygame.mixer.music.play()
                if music in [2, 4, 6, 8, 10, 12, 14, 16]:
                    pygame.mixer.music.stop()

            elif event.key == pygame.K_ESCAPE and (show_firstimage == 1 or show_image >= 1):
                show_game_settings = 1
                show_video = 0


            elif event.key == pygame.K_t:
                show_input = 1

            elif event.key == pygame.K_RETURN:
                show_input = 0

            elif event.key == pygame.K_5:
                if show_firstimage == 1:
                    show_game_settings = 0
                    show_firstimage = 1
                    show_image = 0
                    
                elif show_image == 1:
                    show_game_settings = 0
                    show_image = 1
                    show_firstimage = 0

                elif show_image == 2:
                    show_game_settings = 0
                    show_image = 2
                    show_firstimage = 0

                elif show_image == 3:
                    show_game_settings = 0
                    show_image = 3
                    show_firstimage = 0

                elif show_image == 4:
                    show_game_settings = 0
                    show_image = 4
                    show_firstimage = 0

                elif show_image == 5:
                    show_game_settings = 0
                    show_image = 5
                    show_firstimage = 0

                elif show_image == 6:
                    show_game_settings = 0
                    show_image = 6
                    show_firstimage = 0

                elif show_image == 7:
                    show_game_settings = 0
                    show_image = 7
                    show_firstimage = 0



    # Обновление всех спрайтов
    group.update(event_list)

    # Логика выбора отображаемых элементов
    if show_game_settings == 2:
        screen.fill(WHITE)
        screen.blit(settings_image, (0, 0))

    elif show_game_settings == 1:
        if show_firstimage == 1:
            screen.fill(WHITE)
            screen.blit(image_blur, (0, 0))
            screen.blit(square_surface2, (1100, 500))
            screen.blit(square_surface3, (1100, 700))
            screen.blit(text_surface_pause, text_rect_pause)
            screen.blit(text_surface_pause_settings, text_rect_pause_settings)
       

        elif show_image == 1:
            show_firstimage = 0
            screen.fill(WHITE)
            screen.blit(second_image_blur, (0, 0))
            screen.blit(square_surface2, (1100, 500))
            screen.blit(square_surface3, (1100, 700))
            screen.blit(text_surface_pause, text_rect_pause)
            screen.blit(text_surface_pause_settings, text_rect_pause_settings)
       

        elif show_image == 2:
            show_firstimage = 0
            screen.fill(WHITE)
            screen.blit(third_image_blur, (0, 0))
            screen.blit(square_surface2, (1100, 500))
            screen.blit(square_surface3, (1100, 700))
            screen.blit(text_surface_pause, text_rect_pause)
            screen.blit(text_surface_pause_settings, text_rect_pause_settings)

        elif show_image == 3:
            show_firstimage = 0
            screen.fill(WHITE)
            screen.blit(fourth_image_blur, (0, 0))
            screen.blit(square_surface2, (1100, 500))
            screen.blit(square_surface3, (1100, 700))
            screen.blit(text_surface_pause, text_rect_pause)
            screen.blit(text_surface_pause_settings, text_rect_pause_settings)

        elif show_image == 4:
            show_firstimage = 0
            screen.fill(WHITE)
            screen.blit(fifth_image_blur, (0, 0))
            screen.blit(square_surface2, (1100, 500))
            screen.blit(square_surface3, (1100, 500))
            screen.blit(text_surface_pause, text_rect_pause)
            screen.blit(text_surface_pause_settings, text_rect_pause_settings)

        elif show_image == 5:
            show_firstimage = 0
            screen.fill(WHITE)
            screen.blit(sixth_image_blur, (0, 0))
            screen.blit(square_surface2, (1100, 500))
            screen.blit(square_surface3, (1100, 500))
            screen.blit(text_surface_pause, text_rect_pause)
            screen.blit(text_surface_pause_settings, text_rect_pause_settings)

        elif show_image == 6:
            show_firstimage = 0
            screen.fill(WHITE)
            screen.blit(seventh_image_blur, (0, 0))
            screen.blit(square_surface2, (1100, 500))
            screen.blit(square_surface3, (1100, 500))
            screen.blit(text_surface_pause, text_rect_pause)
            screen.blit(text_surface_pause_settings, text_rect_pause_settings)


        elif show_image == 7:
            show_firstimage = 0
            screen.fill(WHITE)
            screen.blit(eighth_image_blur, (0, 0))
            screen.blit(square_surface2, (1100, 500))
            screen.blit(square_surface3, (1100, 500))
            screen.blit(text_surface_pause, text_rect_pause)
            screen.blit(text_surface_pause_settings, text_rect_pause_settings)

    elif show_image >= 1:
        show_firstimage = 0
        current_time = pygame.time.get_ticks()
        if current_time - image_timer >= image_delay:
            image_index = (image_index + 1) % len(images)  # Переключение на следующее изображение
            image_timer = current_time  # Обновление таймера

        screen.fill(WHITE)
        current_image = images[image_index]

        if isinstance(current_image[0], pygame.Surface):
            screen.blit(current_image[0], (0, 0))  # Отображение изображения
        else:
            screen.blit(current_image, (0, 0))
        if len(current_image) > 1:
            screen.blit(current_image[1], current_image[2])  # Отображение текста

    elif show_video == 1:
        current_time = pygame.time.get_ticks() / 1000
        if current_time <= duration:
            frame_surface = make_frame(current_time)
            screen.blit(frame_surface, (0, 0))
        else:
            show_video = 0
            show_firstimage = 1

    elif show_menu == 1:
        screen.blit(menu_image, (0, 0))
        screen.blit(text_surface_menu_play, text_rect_menu_play)
        screen.blit(text_surface_menu_settings, text_rect_menu_settings)
        screen.blit(text_surface_menu_settings_2, text_rect_menu_settings_2)
        screen.blit(square_surface, (1100, 500))
        screen.blit(square_surface1, (1100, 700))

    elif show_settings == 1:
        screen.fill(WHITE)
        show_menu = 0
        screen.fill((255, 255, 255))
        screen.blit(settings_image, (0, 0))

    elif show_settings == 2:
        show_settings = 0

    elif show_firstimage:
        screen.fill(WHITE)
        screen.blit(image, (0, 0))
        screen.blit(text_surface1, text_rect1)
        image_flag = 1

    if show_settings == 1:
        screen.fill(WHITE)
        show_menu = 0
        screen.fill((255, 255, 255))
        screen.blit(settings_image, (0, 0))

    if show_settings == 2:
        show_settings = 0

    # Вывод введенного текста
    if displayed_text:
        text_surface15 = font_text.render(displayed_text, True, (255, 0, 0))
        text_rect15 = text_surface15.get_rect()
        text_rect15.topleft = (10, 1350)  # Координаты для отображения текста
        screen.blit(text_surface15, text_rect15)

    # Вывод инпут бокса поверх всего остального
    if show_input == 1:
        group.draw(screen)

    # Обновление экрана (ТОЛЬКО ОДИН РАЗ В КОНЦЕ ЦИКЛА)
    pygame.display.flip()

    # Ограничение до 60 FPS
    clock.tick(60)

# Завершение Pygame
pygame.quit()
sys.exit()