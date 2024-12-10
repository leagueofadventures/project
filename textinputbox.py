import pygame
import sys
import time

pygame.init()

# Устанавливаем полноэкранный режим
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
screen_width, screen_height = screen.get_size()

# Цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
LIGHT_GRAY = (210, 210, 210)
DARK_GRAY = (169, 169, 169)

# Заполняем экран белым
screen.fill(WHITE)

# Шрифт для текстового поля
try:
    font = pygame.font.Font(None, 36)
except:
    font = pygame.font.SysFont('Arial', 36)  # Fallback font

# Переменная для сохранения введенного текста
input_text = ""

# Счетчик для обновления
counter = 0

# Флаг для обновления текста
update_text = False

# Класс текстового поля
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
        global update_text  # Declare update_text as global if we're modifying it here
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.rect.collidepoint(event.pos):
                    self.active = True
                else:
                    self.active = False
            if event.type == pygame.KEYDOWN and self.active:
                if event.key == pygame.K_RETURN:
                    global input_text
                    input_text = self.text
                    self.active = False
                    self.text = ""
                    self.render_text()
                    print("Введенный текст:", input_text)
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


# Создаем текстовое поле
text_input_box = TextInputBox(
    screen_width // 2 - 200, screen_height // 2 - 25, 400, font
)
group = pygame.sprite.Group(text_input_box)

# Главный игровой цикл
running = True
start_time = time.time()
clock = pygame.time.Clock()

while running:
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            pygame.quit
            running = False

    current_time = time.time()
    if current_time - start_time >= 1:
        start_time = current_time
        counter += 1
        update_text = True

    group.update(events)

    screen.fill(WHITE)
    group.draw(screen)
    pygame.display.flip()
    clock.tick(60)  # Cap to 60 FPS

print("Введенный текст:", input_text)

pygame.quit()
sys.exit()

