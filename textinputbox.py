import pygame
import sys

pygame.init()

# Устанавливаем полноэкранный режим
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
screen_width, screen_height = screen.get_size()

# Цвета
white = (255, 255, 255)
black = (0, 0, 0)

# Заполняем экран белым
screen.fill(white)

# Шрифт для текстового поля
font = pygame.font.Font(None, 36)  # Стандартный шрифт с размером 36


# Класс текстового поля
class TextInputBox(pygame.sprite.Sprite):
    def __init__(self, x, y, w, font):
        super().__init__()
        self.color = black  # Цвет текста
        self.backcolor = None  # Фон текста (None = прозрачный)
        self.pos = (x, y)  # Позиция текстового поля
        self.width = w  # Ширина текстового поля
        self.font = font  # Шрифт текста
        self.active = False  # Активно ли текстовое поле для ввода
        self.text = ""  # Текущий текст в поле
        self.render_text()  # Создаем изображение текста

    def render_text(self):
        # Рендерим текст
        t_surf = self.font.render(self.text, True, self.color, self.backcolor)
        # Создаем поверхность для текстового поля (с учетом ширины поля и текста)
        self.image = pygame.Surface(
            (max(self.width, t_surf.get_width() + 10), t_surf.get_height() + 10),
            pygame.SRCALPHA,
        )
        # Если задан фон, заполняем его
        if self.backcolor:
            self.image.fill(self.backcolor)
        # Рисуем текст на поверхности
        self.image.blit(t_surf, (5, 5))
        # Рисуем рамку вокруг текстового поля
        pygame.draw.rect(self.image, self.color, self.image.get_rect().inflate(-2, -2), 2)
        # Получаем прямоугольник текстового поля
        self.rect = self.image.get_rect(topleft=self.pos)

    def update(self, event_list):
        # Обрабатываем события
        for event in event_list:
            if event.type == pygame.MOUSEBUTTONDOWN:
                # Если кликнули по текстовому полю, активируем его
                if self.rect.collidepoint(event.pos):
                    self.active = True
                else:
                    self.active = False
            if event.type == pygame.KEYDOWN and self.active:
                if event.key == pygame.K_RETURN:
                    self.active = False  # Деактивируем поле при нажатии Enter
                elif event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]  # Удаляем последний символ
                else:
                    self.text += event.unicode  # Добавляем введенный символ
                self.render_text()  # Обновляем текстовое поле


# Создаем текстовое поле
text_input_box = TextInputBox(
    screen_width // 2 - 200, screen_height // 2 - 25, 400, font
)  # Координаты в центре экрана
group = pygame.sprite.Group(text_input_box)

# Главный игровой цикл
running = True
while running:
    # События
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            running = False

    # Обновляем текстовое поле
    group.update(events)

    # Перерисовываем экран
    screen.fill(white)  # Очищаем экран
    group.draw(screen)  # Рисуем текстовое поле
    pygame.display.flip()  # Обновляем экран

pygame.quit()
sys.exit()
