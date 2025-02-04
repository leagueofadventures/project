import pygame
import os
import math
import random
import numpy as np
import pickle
import socket
import threading
import json
import select  # Добавляем модуль select для работы с неблокирующими сокетами


# Инициализация Pygame
pygame.init()
print("Pygame успешно инициализирован")

# Установка размеров окна
screen_width = 1920
screen_height = 1080
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Gambit - Multiplayer')
print("Окно успешно создано")
# Инициализация переменных игрока
player_hitbox_offset_x = 10  # Смещение хитбокса по X
player_hitbox_offset_y = 10  # Смещение хитбокса по Y


# Определение путей
image_path = 'images/'

# Инициализация карты
map_width = 3000
map_height = 2000
camera_x = 0
camera_y = 0

# Игровые состояния
GAME_PLAYING = 0
GAME_OVER_WIN = 1
GAME_OVER_LOSE = 2
game_state = GAME_PLAYING
current_level = 100000

# Игроки
player_health = 100
player_max_health = 100
player_shoot_delay = 30
player_shoot_timer = 0
player_hit_cooldown = 0
player_hit_cooldown_max = 30
player_speed_multiplier = 1.0
player_damage_multiplier = 1.0
player_position = [[map_width // 2, map_height // 2], [map_width // 2 - 100, map_height // 2 - 100]]  # Позиции двух игроков

# Игровые объекты
enemies = []
bullets = []
player_bullets = []

# Основные параметры
base_speed = 5
clock = pygame.time.Clock()
game_speed = 1.0
upgrade_choice = None  # Переменная для хранения выбора улучшения
running = True


# Функция для запуска серверного игрового цикла в отдельном потоке
def run_server_game_loop(conn):
    threading.Thread(target=server_game_loop, args=(conn,), daemon=True).start()

# Функция для запуска клиентского игрового цикла в отдельном потоке
def run_client_game_loop(client):
    threading.Thread(target=client_game_loop, args=(client,), daemon=True).start()
class Enemy:
    def __init__(self, x, y, level=1, enemy_type='basic'):
        self.x = x
        self.y = y
        self.level = level
        self.enemy_type = enemy_type
        self.size = 30  # Размер врага
        self.shoot_delay = 90  # Задержка между выстрелами (в кадрах)
        self.shoot_timer = 0
        self.speed = 1.0
        self.damage = 10
        self.health = 100 * level

        # Настройки врага в зависимости от его типа
        if self.enemy_type == 'basic':
            self.color = (255, 0, 0)  # Красный враг
            self.speed = 1.5
            self.damage = 10
        elif self.enemy_type == 'fast':
            self.color = (0, 255, 0)  # Зелёный враг
            self.speed = 2.5
            self.damage = 7
            self.health = 70 * level
        elif self.enemy_type == 'tank':
            self.color = (0, 0, 255)  # Синий враг
            self.speed = 1.0
            self.damage = 20
            self.health = 200 * level

    def move_towards_player(self, player_x, player_y):
        """
        Двигает врага в направлении игрока.
        """
        dx = player_x - self.x
        dy = player_y - self.y
        dist = math.sqrt(dx ** 2 + dy ** 2)
        if dist > 0:
            dx /= dist
            dy /= dist
        self.x += dx * self.speed
        self.y += dy * self.speed

    def draw(self, surface):
        """
        Отображает врага на экране.
        """
        pygame.draw.rect(surface, self.color, (self.x - camera_x, self.y - camera_y, self.size, self.size))

    def take_damage(self, damage):
        """
        Уменьшает здоровье врага при получении урона.
        """
        self.health -= damage
        if self.health <= 0:
            return True  # Враг уничтожен
        return False

    def should_shoot(self):
        """
        Определяет, должен ли враг стрелять.
        """
        if self.shoot_timer <= 0:
            self.shoot_timer = self.shoot_delay
            return True
        else:
            self.shoot_timer -= 1
            return False
def create_enemies(level):
    """
    Создаёт врагов для текущего уровня.
    :param level: Уровень игры.
    :return: Список врагов.
    """
    num_enemies = 5 + (level - 1) * 3  # Увеличиваем количество врагов с каждым уровнем
    types = ['basic', 'fast', 'tank']  # Типы врагов
    new_enemies = []

    for _ in range(num_enemies):
        enemy_type = random.choice(types)  # Случайно выбираем тип врага
        temp_enemy = Enemy(0, 0, level, enemy_type)  # Создаём временного врага для получения его размера
        x = random.randint(0, map_width - temp_enemy.size)  # Случайная позиция по X
        y = random.randint(0, map_height - temp_enemy.size)  # Случайная позиция по Y
        new_enemies.append(Enemy(x, y, level, enemy_type))  # Создаём врага с заданными координатами

    return new_enemies
class Bullet:
    def __init__(self, x, y, target_x, target_y, speed=7, is_player_bullet=False, homing=False, target_enemy=None, damage=10):
        """
        Инициализация пули.
        :param x: Начальная позиция пули по X.
        :param y: Начальная позиция пули по Y.
        :param target_x: Координата цели по X.
        :param target_y: Координата цели по Y.
        :param speed: Скорость пули.
        :param is_player_bullet: Является ли пуля выпущенной игроком.
        :param homing: Является ли пуля самонаводящейся.
        :param target_enemy: Цель для самонаводящейся пули.
        :param damage: Урон, наносимый пулей при попадании.
        """
        self.x = x
        self.y = y
        self.speed = speed
        self.is_player_bullet = is_player_bullet
        self.radius = 5 if not is_player_bullet else 10  # Размер пули зависит от того, кто стреляет
        self.color = (255, 0, 0) if not is_player_bullet else (0, 255, 0)  # Цвет пули
        self.homing = homing
        self.target_enemy = target_enemy
        self.damage = damage

        # Вычисляем направление полёта пули
        self.dx, self.dy = self.calculate_trajectory(target_x, target_y)

    def calculate_trajectory(self, target_x, target_y):
        """
        Вычисляет направление движения пули.
        :param target_x: Координата цели по X.
        :param target_y: Координата цели по Y.
        :return: Нормализованные значения dx и dy.
        """
        dx = target_x - self.x
        dy = target_y - self.y
        distance = math.sqrt(dx ** 2 + dy ** 2)
        if distance == 0:  # Если расстояние до цели равно 0
            return 0, 0
        return dx / distance * self.speed, dy / distance * self.speed

    def move(self):
        """
        Обновляет положение пули.
        """
        # Если пуля самонаводящаяся, обновляем направление к цели
        if self.homing and self.target_enemy and self.target_enemy.health > 0:
            self.dx, self.dy = self.calculate_trajectory(
                self.target_enemy.x + self.target_enemy.size / 2,
                self.target_enemy.y + self.target_enemy.size / 2
            )
        self.x += self.dx
        self.y += self.dy

    def draw(self, surface):
        """
        Отрисовывает пулю на экране.
        :param surface: Поверхность для отрисовки.
        """
        pygame.draw.circle(surface, self.color, (int(self.x - camera_x), int(self.y - camera_y)), self.radius)

    def get_rect(self):
        """
        Возвращает прямоугольник, описывающий пулю (для проверки столкновений).
        :return: pygame.Rect.
        """
        return pygame.Rect(self.x - self.radius, self.y - self.radius, self.radius * 2, self.radius * 2)

def draw_menu():
    """
    Отображает главное меню с выбором режима игры.
    """
    screen.fill((0, 0, 0))
    font = pygame.font.Font(None, 74)
    title_text = font.render('Gambit - Multiplayer', True, (255, 255, 255))
    offline_text = pygame.font.Font(None, 50).render('1. Играть оффлайн', True, (0, 255, 0))
    online_text = pygame.font.Font(None, 50).render('2. Играть онлайн', True, (0, 255, 0))

    screen.blit(title_text, (screen_width // 2 - title_text.get_width() // 2, screen_height // 4))
    screen.blit(offline_text, (screen_width // 2 - offline_text.get_width() // 2, screen_height // 2))
    screen.blit(online_text, (screen_width // 2 - online_text.get_width() // 2, screen_height // 2 + 100))

    pygame.display.flip()

def start_server():
    """
    Запускает сервер для онлайн-игры и выводит IP-адрес сервера.
    """
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Повторное использование адреса
    server.bind(('0.0.0.0', 5555))
    server.listen(1)

    # Получаем локальный IP-адрес
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)

    print(f"Сервер запущен!")
    print(f"IP-адрес сервера: {local_ip}")
    print(f"Ожидание подключения клиента...")

    # Добавим серверный сокет в список для мониторинга
    inputs = [server]
    outputs = []

    conn = None  # Переменная для хранения соединения с клиентом

    while True:
        # Используем select для отслеживания активности на сокетах
        readable, writable, exceptional = select.select(inputs, outputs, inputs)

        for s in readable:
            if s is server:
                # Новое входящее соединение
                conn, addr = server.accept()
                print(f"Клиент подключён: {addr}")
                conn.setblocking(False)
                inputs.append(conn)  # Добавляем клиентский сокет в список для мониторинга
            else:
                # Получение данных от клиента
                try:
                    data = s.recv(2048).decode('utf-8')
                    if data:
                        print(f"Получены данные от клиента: {data}")
                        return conn  # Возвращаем соединение для дальнейшей обработки
                except BlockingIOError:
                    pass  # Неблокирующий режим: продолжаем выполнение


    
def start_client():
    """
    Подключается к серверу для онлайн-игры.
    """
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.setblocking(False)  # Делаем клиентский сокет неблокирующим

    server_ip = input("Введите IP сервера: ")
    try:
        client.connect((server_ip, 5555))
    except BlockingIOError:
        # Неблокирующий режим: connect может бросить исключение
        pass

    print(f"Подключение к серверу {server_ip}...")
    return client


# Отправка состояния игры
def send_game_state(connection, game_state):
    try:
        connection.send(json.dumps(game_state).encode('utf-8'))
    except Exception as e:
        print(f"Ошибка отправки данных: {e}")

# Получение состояния игры
def receive_game_state(connection):
    try:
        data = connection.recv(2048).decode('utf-8')
        return json.loads(data)
    except Exception as e:
        print(f"Ошибка получения данных: {e}")
        return None

# Отправка действий игрока
def send_player_action(connection, action):
    try:
        connection.send(json.dumps(action).encode('utf-8'))
    except Exception as e:
        print(f"Ошибка отправки действий: {e}")
def server_game_loop(conn):
    """
    Основной игровой цикл для сервера. Управляет логикой игры и отправляет клиенту состояние игры.
    """
    global enemies, player_position, bullets, player_bullets, running

    print("Запущен серверный игровой цикл.")
    while running:
        # Получение действий клиента
        try:
            client_action = conn.recv(2048).decode('utf-8')
            if client_action:
                action = json.loads(client_action)
                if 'move' in action:
                    # Обновляем позицию второго игрока (клиента)
                    player_position[1][0] += action['move'][0]
                    player_position[1][1] += action['move'][1]
        except BlockingIOError:
            # Нет данных от клиента, пропускаем
            pass
        except Exception as e:
            print(f"Ошибка в серверном цикле: {e}")
            break

        # --- Обновление врагов ---
        for enemy in enemies:
            enemy.move_towards_player(player_position[0][0], player_position[0][1])

        # --- Отправка состояния клиенту ---
        try:
            game_state = {
                'enemies': [[enemy.x, enemy.y, enemy.health] for enemy in enemies],
                'player1': player_position[0],
                'player2': player_position[1],
                'bullets': [[bullet.x, bullet.y] for bullet in bullets]
            }
            conn.send(json.dumps(game_state).encode('utf-8'))
        except BlockingIOError:
            pass  # Неблокирующий режим: пропускаем, если клиент не готов принять данные
        except Exception as e:
            print(f"Ошибка при отправке данных клиенту: {e}")
            break

        # Ограничение FPS
        pygame.time.delay(16)  # ~60 FPS


def client_game_loop(client):
    """
    Основной игровой цикл клиента. Получает состояние игры от сервера и отправляет свои действия.
    """
    global enemies, player_position, bullets, player_bullets, running

    print("Запущен клиентский игровой цикл.")
    while running:
        # --- Отправка действий игрока серверу ---
        keys = pygame.key.get_pressed()
        move_x, move_y = 0, 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            move_x -= 5
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            move_x += 5
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            move_y -= 5
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            move_y += 5
        action = {'move': [move_x, move_y]}
        try:
            client.send(json.dumps(action).encode('utf-8'))
        except BlockingIOError:
            # Если сервер не готов принять данные, пропускаем
            pass

        # --- Получение состояния игры от сервера ---
        try:
            game_state = client.recv(2048).decode('utf-8')
            if game_state:
                game_state = json.loads(game_state)
                # Обновляем врагов
                enemies = [Enemy(x, y, health=health) for x, y, health in game_state['enemies']]
                # Обновляем позиции игроков
                player_position[0] = game_state['player1']
                player_position[1] = game_state['player2']
                # Обновляем пули
                bullets = [Bullet(x, y, 0, 0) for x, y in game_state['bullets']]
        except BlockingIOError:
            # Нет данных от сервера, пропускаем
            pass
        except Exception as e:
            print(f"Ошибка в клиентском цикле: {e}")
            break

        # Ограничение FPS
        pygame.time.delay(16)  # ~60 FPS
        
def offline_game_loop():
    """
    Основной игровой цикл для оффлайн-режима.
    """
    global running, enemies, player_position, bullets, player_bullets, player_health, current_level

    # Создаём врагов для текущего уровня
    enemies = create_enemies(current_level)
    player_health = player_max_health  # Восстанавливаем здоровье игрока

    while running:
        # Обработка событий
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # --- Движение игрока ---
        keys = pygame.key.get_pressed()
        move_x, move_y = 0, 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            move_x -= base_speed * player_speed_multiplier
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            move_x += base_speed * player_speed_multiplier
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            move_y -= base_speed * player_speed_multiplier
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            move_y += base_speed * player_speed_multiplier

        # Обновляем позицию игрока
        player_position[0][0] += move_x
        player_position[0][1] += move_y

        # Ограничение позиции игрока внутри карты
        player_position[0][0] = max(0, min(player_position[0][0], map_width - 50))
        player_position[0][1] = max(0, min(player_position[0][1], map_height - 50))

        # --- Обновление врагов ---
        for enemy in enemies[:]:
            enemy.move_towards_player(player_position[0][0], player_position[0][1])

            # Враг стреляет
            if enemy.should_shoot():
                bullets.append(Bullet(
                    enemy.x + enemy.size / 2,
                    enemy.y + enemy.size / 2,
                    player_position[0][0],
                    player_position[0][1],
                    speed=5,
                    is_player_bullet=False
                ))

            # Удаляем врага, если здоровье <= 0
            if enemy.health <= 0:
                enemies.remove(enemy)

        # --- Обновление пуль ---
        for bullet in bullets[:]:
            bullet.move()
            # Удаляем пулю, если она выходит за границы карты
            if bullet.x < 0 or bullet.x > map_width or bullet.y < 0 or bullet.y > map_height:
                bullets.remove(bullet)
            else:
                # Проверка попадания пули в игрока
                player_rect = pygame.Rect(
                    player_position[0][0] + player_hitbox_offset_x,
                    player_position[0][1] + player_hitbox_offset_y,
                    50 - 2 * player_hitbox_offset_x,
                    50 - 2 * player_hitbox_offset_y
                )
                if not bullet.is_player_bullet and bullet.get_rect().colliderect(player_rect):
                    player_health -= 10  # Урон игроку
                    bullets.remove(bullet)
                    if player_health <= 0:
                        print("Вы проиграли!")
                        return  # Завершаем игру, если игрок умер

                # Проверка попадания пули во врагов
                for enemy in enemies[:]:
                    if bullet.is_player_bullet and bullet.get_rect().colliderect(enemy.get_rect()):
                        enemy.take_damage(10)  # Урон врагу
                        bullets.remove(bullet)
                        break

        # --- Проверка выигрыша ---
        if len(enemies) == 0:
            print(f"Уровень {current_level} завершён!")
            current_level += 1
            enemies = create_enemies(current_level)  # Переход на следующий уровень

        # --- Отрисовка ---
        screen.fill((0, 0, 0))  # Очистка экрана

        # Отрисовка врагов
        for enemy in enemies:
            enemy.draw(screen)

        # Отрисовка пуль
        for bullet in bullets:
            bullet.draw(screen)

        # Отрисовка игрока
        pygame.draw.rect(screen, (0, 255, 0), (
            player_position[0][0] - camera_x, player_position[0][1] - camera_y, 50, 50))  # Зелёный квадрат игрока

        # Отрисовка полоски здоровья игрока
        health_bar_width = 50
        health_bar_height = 5
        health_percentage = player_health / player_max_health
        pygame.draw.rect(screen, (255, 0, 0), (
            player_position[0][0] - camera_x, player_position[0][1] - camera_y - 10, health_bar_width, health_bar_height))
        pygame.draw.rect(screen, (0, 255, 0), (
            player_position[0][0] - camera_x, player_position[0][1] - camera_y - 10,
            health_bar_width * health_percentage, health_bar_height))

        # Отображение количества врагов
        font = pygame.font.Font(None, 36)
        enemy_count_text = font.render(f'Враги: {len(enemies)}', True, (255, 255, 255))
        screen.blit(enemy_count_text, (10, 10))

        # Обновление экрана
        pygame.display.flip()

        # Ограничение FPS
        clock.tick(60)

# Главное меню
while True:
    draw_menu()  # Отображение меню
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_1:  # Оффлайн режим
                print("Запуск оффлайн-игры...")
                offline_game_loop()  # Переходим в оффлайн игровой цикл
                running = False
            elif event.key == pygame.K_2:  # Онлайн режим
                mode = input("Вы хотите быть сервером (s) или клиентом (c)? ")
                if mode.lower() == 's':
                    conn = start_server()
                    server_game_loop(conn)
                elif mode.lower() == 'c':
                    client = start_client()
                    if client:
                        client_game_loop(client)
