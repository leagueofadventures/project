
import pygame
from pygame.locals import *
import sys
import time 
from moviepy.editor import VideoFileClip


# класс для инпут бокса
class TextInputBox(pygame.sprite.Sprite):
    def __init__(self, x, y, w, font):
        super().__init__()
        self.color = (0, 0, 0)
        self.backcolor = None
        self.pos = (x, y) 
        self.width = w
        self.font = font
        self.active = False
        self.text = ""
        self.render_text()

    def render_text(self):


        t_surf = self.font.render(self.text, True, self.color, self.backcolor)
        self.image = pygame.Surface((max(self.width, t_surf.get_width()+10), t_surf.get_height()+10), pygame.SRCALPHA)
        if self.backcolor:
            self.image.fill(self.backcolor)
        self.image.blit(t_surf, (5, 5))
        pygame.draw.rect(self.image, self.color, self.image.get_rect().inflate(-2, -2), 2)
        self.rect = self.image.get_rect(topleft=self.pos)

    def update(self, event_list):
        for event in event_list:
            if event.type == pygame.MOUSEBUTTONDOWN:
                # Если кликаем на текстовое поле, активируем его
                if self.rect.collidepoint(event.pos):
                    self.active = True
                else:
                    self.active = False
            if event.type == pygame.KEYDOWN and self.active:
                if event.key == pygame.K_RETURN:
                    self.active = False
                elif event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]

                else:
                    self.text += event.unicode
                self.render_text()




# Инициализация Pygame
pygame.init()

pygame.mixer.init()
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)  # Установите разрешение по необходимости




# параметры текста в инпут
font = pygame.font.SysFont(None, 32)  # Размер шрифта уменьшен для примера
clock = pygame.time.Clock()
text_input_box = TextInputBox(1800, 1250, 400, font)  # Координаты внутри экрана
group = pygame.sprite.Group(text_input_box)

# Загрузка изображения (убедитесь, что файл "1.png" существует)
try:
    image = pygame.image.load("1.png")
    settings_image = pygame.image.load('Settings.png')
    menu_image = pygame.image.load('menu.jpg')
    second_image = pygame.image.load('2.png')
    pygame.mixer.music.load('12.mp3')
except pygame.error:
    image = None
    print("Не удалось загрузить изображение '1.png'.")
    
    
# Загрузка видеофайла
clip = VideoFileClip('video.mp4')
video_width, video_height = clip.size
duration = clip.duration

    
settings_image_rect = settings_image.get_rect()

image_rect = image.get_rect()

second_image_rect = second_image.get_rect()

menu_image_rect = menu_image.get_rect()



  # Передний план центрируется

# параметры текста
font_text = pygame.font.Font(None, 50)
font_text1 = pygame.font.Font(None, 35)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = ( 66,170,255)


text_surface = font_text.render('Однажды в одном мире зародилась жизнь', True, BLACK)
text_rect = text_surface.get_rect()
text_rect.topleft = (10, 1300)# Пример координат


text_surface1 = font_text.render('Настройки', True, BLACK, WHITE)
text_rect1 = text_surface1.get_rect()
text_rect1.topleft = (1200, 400)# Пример координат


text_surface2 = font_text1.render('Для вывода следующего изображения нажмите "пробел"', True, BLACK, WHITE)
text_rect2 = text_surface1.get_rect()
text_rect2.topleft = (100, 500)# Пример координат


text_surface3 = font_text1.render('Для ввода текста нажмите "t"', True, BLACK, WHITE)
text_rect3 = text_surface1.get_rect()
text_rect3.topleft = (100, 550)# Пример координат

text_surface4 = font_text1.render('Для повторного открытия настроек нажмите "esc"', True, BLACK, WHITE)
text_rect4 = text_surface1.get_rect()
text_rect4.topleft = (1500, 500)# Пример координат

text_surface5 = font_text1.render('Для закрытия настроек после вывода изображения нажмите "esc"', True, BLACK, WHITE)
text_rect5 = text_surface1.get_rect()
text_rect5.topleft = (1500, 550)# Пример координат

text_surface6 = font_text1.render('Чтобы играть, нажмите 1', True, BLACK, WHITE)
text_rect6 = text_surface1.get_rect()
text_rect6.topleft = (1150, 550)# Пример координат

text_surface7 = font_text1.render('Чтобы зайти в настройки,', True, BLACK, WHITE)
text_rect7 = text_surface1.get_rect()
text_rect7.topleft = (1150, 750)# Пример координат

text_surface8 = font_text1.render('нажмите 2', True, BLACK, WHITE)
text_rect8 = text_surface1.get_rect()
text_rect8.topleft = (1230, 790)# Пример координат

text_surface9 = font_text1.render('Здравствуй незнакомец, на нашу деревню напали варвары, помоги нам защитить нашу деревню от них!', True, BLACK)
text_rect9 = text_surface1.get_rect()
text_rect9.topleft = (400, 1260)# Пример координат

text_surface10 = font_text1.render('В ней появились разные существа. Одни были злые другие добрые а некоторые вообще не относились ни к первым ни к другим.', True, BLACK)
text_rect10 = text_surface1.get_rect()
text_rect10.topleft = (10, 1300)# Пример координат

text_surface11 = font_text1.render('Хорошо. Расскажи мне, что происходит', True, BLACK)
text_rect11 = text_surface1.get_rect()
text_rect11.topleft = (200, 1260)# Пример координат







# Установка прозрачности (alpha). 128 — это значение для полупрозрачности (50%).
alpha = 128

# Создание поверхности (surface) размером 200x200 с альфа-каналом
square_surface = pygame.Surface((400, 150), pygame.SRCALPHA)

square_surface1 = pygame.Surface((400, 150), pygame.SRCALPHA)

# Заполнение поверхности полупрозрачным цветом (например, красным)
# (R, G, B, alpha)
square_surface.fill((255, 255, 255, alpha))

square_surface1.fill((255, 255, 255, alpha))


def make_frame(t):
    frame = clip.get_frame(t)
    # Преобразование кадра видео в изображение Pygame
    surf = pygame.surfarray.make_surface(frame.swapaxes(0, 1))
    return surf

running = True

show_text = 0

show_settings = 0

show_input = 0

show_video = 0


show_menu = 1

show_firstimage = 0
music = 0


show_image = 0



screen.fill(WHITE)
while running:
    event_list = pygame.event.get()
    for event in event_list:
        if event.type == QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            
            if event.key == pygame.K_SPACE:
                show_firstimage = 0
                show_image = 1
                show_menu = 0
                
            elif event.key == pygame.K_1:
                show_video = 1
                
            elif event.key == pygame.K_2:
                show_settings = 1
                if show_menu == 0:
                    show_settings = 2
                    show_menu = 1


            elif event.key == pygame.K_3:
                music += 1
                pygame.mixer.music.play()
                if music == 2 or music == 4 or music == 6 or music == 8 or music == 10 or music == 12 or music == 14 or music == 16:
                    pygame.mixer.music.stop()
    
                
                

                
            elif event.key == pygame.K_ESCAPE:
                show_settings = 2
                show_menu = 0
                    
            elif event.key == pygame.K_t:
                show_input = 1
                
            elif event.key == pygame.K_RETURN:
                show_input = 0

    # Обновление всех спрайтов
    group.update(event_list)
        




    # Получение следующего кадра видео

        

  
    if show_image == 1:
        screen.fill(WHITE)
        screen.blit(text_surface10, text_rect10)
        screen.blit(second_image, (0, 0))
    pygame.display.flip()
    
    
    # вывод первого изображения 

   


     
    if show_firstimage:
        screen.fill(WHITE)
        screen.blit(image, (0, 0))
        screen.blit(text_surface, text_rect)


    if show_settings == 2:
        show_settings = 0
    


    if show_video == 1:


        show_menu = 0

        current_time = pygame.time.get_ticks() / 1000
        if current_time <= duration:
                frame_surface = make_frame(current_time)
                screen.blit(frame_surface, (0, 0))
  

        show_firstimage = 1


    if show_settings == 2:
        show_menu = 1
        screen.blit(menu_image, (0, 0))
        screen.blit(text_surface6, text_rect6)
        screen.blit(text_surface7, text_rect7)
        screen.blit(text_surface8, text_rect8)
        screen.blit(square_surface, (1100, 500))
        screen.blit(square_surface1, (1100, 700))

   
    
    # вывод инпут бокса
    if show_input == 1:
        group.draw(screen)


        
    if show_menu == 1:
        screen.blit(menu_image, (0, 0))
        screen.blit(text_surface6, text_rect6)
        screen.blit(text_surface7, text_rect7)
        screen.blit(text_surface8, text_rect8)
        screen.blit(square_surface, (1100, 500))
        screen.blit(square_surface1, (1100, 700))


        
    if show_settings == 1:
        show_menu = 0
        screen.fill((255, 255, 255))
        screen.blit(settings_image, (0, 0))
    
    # вывод текста
   

    
    
    
    
   
    # вывод настроек 
   

  
clock.tick(60)  # Ограничение до 60 FPS
    
pygame.display.flip()
    

    
pygame.quit()
sys.exit()
