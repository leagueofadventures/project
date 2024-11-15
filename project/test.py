import pygame
import sys

# Инициализация Pygame
pygame.init()

# Создание окна
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)

image = pygame.image.load('settings.png')


# Установка прозрачности (alpha). 128 — это значение для полупрозрачности (50%).
alpha = 128

# Создание поверхности (surface) размером 200x200 с альфа-каналом
square_surface = pygame.Surface((200, 200), pygame.SRCALPHA)

# Заполнение поверхности полупрозрачным цветом (например, красным)
# (R, G, B, alpha)
square_surface.fill((255, 0, 0, alpha))
flip = True
# Основной цикл игры
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

 
    # Очистка экрана
    screen.fill((255, 255, 255))

    screen.blit(image, (100, 100))  # Отображаем изображение в позиции (100, 100)

    # Отображение полупрозрачного квадрата
    screen.blit(square_surface, (200, 500))

    # Обновление экрана
    if flip:
        pygame.display.flip()
        flip = False
        
# Завершение Pygame
pygame.quit()
