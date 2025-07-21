import pygame
import sys
from awareness import Awareness
from gemini_api import GeminiAPI
from state_controller import StateController

# Инициализация Pygame
pygame.init()

# Размеры окна
WIDTH, HEIGHT = 1280, 720
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("2D мир Зорины")

# Цвета
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BACKGROUND_COLOR = (30, 30, 30)
INPUT_BOX_COLOR_ACTIVE = (50, 50, 50)
INPUT_BOX_COLOR_INACTIVE = (70, 70, 70)
BUTTON_COLOR = (70, 130, 180)
BUTTON_HOVER_COLOR = (100, 160, 210)

# Шрифт для отображения текста
font = pygame.font.SysFont("monospace", 16)

# Создаем объекты Awareness, GeminiAPI и StateController
zorina = Awareness()
gemini = GeminiAPI()
state_controller = StateController()

# Позиция Зорины в 2D мире
zorina_pos = (WIDTH // 2, HEIGHT - 260)

# Ввод текста
input_box = pygame.Rect(20, HEIGHT - 40, WIDTH - 40, 30)
input_active = False
user_text = ""

# История чата (списки кортежей (speaker, text))
chat_history = []

# Текущий отображаемый ответ Зорины для эффекта печати
zorina_display_text = ""
zorina_full_text = ""
zorina_text_index = 0
zorina_typing = False
zorina_last_update = 0
zorina_typing_speed = 30  # миллисекунд на символ

# Кнопка "Покормить"
feed_button = pygame.Rect(WIDTH - 120, HEIGHT - 200, 100, 40)

# Функция для отображения многострочного текста с переносом
def wrap_text(text, font, max_width):
    words = text.split(' ')
    lines = []
    current_line = ""
    for word in words:
        test_line = current_line + word + " "
        if font.size(test_line)[0] <= max_width:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word + " "
    lines.append(current_line)
    return lines

# Функция для отображения многострочного текста с переносом
def wrap_text(text, font, max_width):
    words = text.split(' ')
    lines = []
    current_line = ""
    for word in words:
        test_line = current_line + word + " "
        if font.size(test_line)[0] <= max_width:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word + " "
    lines.append(current_line)
    return lines

# Функция для отображения истории чата (без пользовательских сообщений)
def draw_chat_history(surface, chat, font, start_x, start_y, max_width, max_lines):
    y_offset = start_y
    lines_drawn = 0
    for speaker, text in reversed(chat):
        if speaker == "Я":
            continue  # не отображать реплики пользователя
        wrapped_lines = wrap_text(text, font, max_width)
        # Объединяем все строки обратно в один текст с переносами
        full_text = "\n".join(line.strip() for line in wrapped_lines)
        display_text = f"{speaker}: {full_text}"
        text_lines = display_text.split('\n')
        for line in reversed(text_lines):
            if lines_drawn >= max_lines:
                return
            text_surface = font.render(line, True, WHITE)
            surface.blit(text_surface, (start_x, y_offset))
            y_offset -= 20
            lines_drawn += 1

# Основной цикл программы
clock = pygame.time.Clock()
running = True
while running:
    current_time = pygame.time.get_ticks()

    # Обновляем состояния Зорины регулярно
    state_controller.update_states()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            # Активируем поле ввода при клике
            if input_box.collidepoint(event.pos) and not zorina_typing:
                input_active = True
            else:
                input_active = False
            # Обработка клика по кнопке "Покормить"
            if feed_button.collidepoint(event.pos):
                feed_result = state_controller.feed()
                chat_history.append(("Система", feed_result))
        elif event.type == pygame.KEYDOWN and input_active and not zorina_typing:
            if event.key == pygame.K_RETURN:
                if user_text.strip():
                    # Добавляем ввод пользователя в историю (но не отображаем)
                    chat_history.append(("Я", user_text.strip()))

                    # Обработка команды памяти
                    command_result = zorina.memory_controller.process_command(user_text.strip())
                    if command_result:
                        chat_history.append(("Система", command_result))
                        zorina_display_text = command_result
                        zorina_typing = False
                    else:
                        if state_controller.is_dead:
                            answer = "Она умерла... Уже поздно... Как это? довести до смерти девочку..."
                            zorina_full_text = answer
                            zorina_display_text = ""
                            zorina_text_index = 0
                            zorina_typing = True
                            zorina_last_update = current_time
                            chat_history.append(("Зорина", answer))
                        else:
                            # Формируем контекст и запрос для GeminiAPI
                            personality = zorina.get_personality_description()
                            memory_context = zorina.get_context()
                            # Получаем текущее настроение из контроллера состояний
                            emotion = state_controller.mood.state
                            emotion_context = f"Текущее настроение Зорины: {emotion}"

                            # Обновляем состояние общения при вводе пользователя
                            state_controller.communicate()

                            # Получаем текущие состояния
                            states = state_controller.get_status()
                            states_description = (
                                f"Сытость: {int(states['satiety'])}, "
                                f"Общение: {int(states['communication'])}, "
                                f"Психологическое состояние: {int(states['psychological'])}, "
                                f"Настроение: {states['mood']}."
                            )
                            # Определяем, какие состояния нужно восполнить
                            needs_replenish = []
                            if states['satiety'] <= 50:
                                needs_replenish.append("сытость")
                            if states['communication'] <= 50:
                                needs_replenish.append("общение")
                            if states['psychological'] <= 50:
                                needs_replenish.append("психологическое состояние")
                            needs_replenish_str = ", ".join(needs_replenish) if needs_replenish else "ничего"

                            prompt = (
                                f"{personality}\n"
                                f"{memory_context}\n"
                                f"{emotion_context}\n"
                                f"Текущие состояния Зорины: {states_description}\n"
                                f"Если какое-либо состояние ({needs_replenish_str}) ниже или равно 50, Зорина должна попросить восполнить его. "
                                f"Если все состояния выше 50, Зорина не должна просить восполнить их.\n"
                                f"Отвечай максимально человечно и естественно, формулируй ответ в пределах 150 символов, "
                                f"и чтобы реплики соответствовали текущему настроению Зорины.\n"
                                f"Вопрос: {user_text.strip()}"
                            )
                            try:
                                response = gemini.generate_content(prompt)
                                content = response.get("candidates", [{}])[0].get("content", {})
                                parts = content.get("parts", [])
                                answer = ""
                                if parts and isinstance(parts, list):
                                    answer = "".join(part.get("text", "") for part in parts)
                                if not answer:
                                    answer = str(response)
                            except Exception as e:
                                answer = f"Ошибка при вызове Gemini API: {e}"

                            # Запускаем эффект печати для ответа Зорины
                            zorina_full_text = answer
                            zorina_display_text = ""
                            zorina_text_index = 0
                            zorina_typing = True
                            zorina_last_update = current_time

                            # Добавляем ответ в историю (для логики, но не отображаем пока)
                            chat_history.append(("Зорина", answer))
                            # Добавляем в память
                            zorina.add_to_memory(user_text.strip(), answer)

                        user_text = ""
            elif event.key == pygame.K_BACKSPACE:
                user_text = user_text[:-1]
            else:
                user_text += event.unicode

    # Обновление текста с эффектом печати
    if zorina_typing:
        if current_time - zorina_last_update > zorina_typing_speed:
            if zorina_text_index < len(zorina_full_text):
                zorina_display_text += zorina_full_text[zorina_text_index]
                zorina_text_index += 1
                zorina_last_update = current_time
            else:
                zorina_typing = False

    # Заполнение фона
    # screen.fill(BACKGROUND_COLOR)

    # Загружаем и отображаем фон из файла
    background = pygame.image.load("texture/room.jpg")
    background = pygame.transform.scale(background, (WIDTH, HEIGHT))
    screen.blit(background, (0, 0))

    # Загружаем и отображаем спрайт Зорины
    zorina_sprite = pygame.image.load("texture/zorina.png")
    zorina_sprite = pygame.transform.scale(zorina_sprite, (zorina_sprite.get_width() // 2, zorina_sprite.get_height() // 2))
    sprite_rect = zorina_sprite.get_rect(center=zorina_pos)
    screen.blit(zorina_sprite, sprite_rect)

    # Отображаем историю чата слева внизу (без пользовательских сообщений)
    # Уберем отображение ответа Зорины из истории, чтобы не дублировался
    filtered_chat_history = [(speaker, text) for speaker, text in chat_history if speaker != "Зорина"]
    draw_chat_history(screen, filtered_chat_history, font, 20, HEIGHT - 60, WIDTH - 40, 20)

    # Отображаем окно с ответом Зорины над полем ввода с увеличенной скругленной рамкой
    response_box = pygame.Rect(20, HEIGHT - 110, WIDTH - 40, 60)
    border_radius = 15
    pygame.draw.rect(screen, (50, 50, 50), response_box, border_radius=border_radius)
    # Убираем символы переноса строки \n из отображаемого текста
    clean_display_text = zorina_display_text.replace("\\n", " ").replace("\n", " ")
    response_lines = wrap_text(clean_display_text, font, response_box.width - 20)
    y_offset = response_box.y + 10
    for line in response_lines:
        text_surface = font.render(line, True, WHITE)
        screen.blit(text_surface, (response_box.x + 10, y_offset))
        y_offset += 20

    # Отображаем поле ввода
    box_color = INPUT_BOX_COLOR_ACTIVE if input_active else INPUT_BOX_COLOR_INACTIVE
    pygame.draw.rect(screen, box_color, input_box)
    input_surface = font.render(user_text, True, WHITE)
    screen.blit(input_surface, (input_box.x + 5, input_box.y + 5))

    # Отображаем эмоцию Зорины в левом верхнем углу
    emotion_box = pygame.Rect(20, 20, 200, 40)
    pygame.draw.rect(screen, (70, 70, 70), emotion_box, border_radius=10)
    emotion_text = state_controller.mood.state
    emotion_surface = font.render(f"Эмоция: {emotion_text}", True, WHITE)
    screen.blit(emotion_surface, (emotion_box.x + 10, emotion_box.y + 10))

    # Отображаем состояния Зорины в правом верхнем углу
    status_box = pygame.Rect(WIDTH - 220, 20, 200, 100)
    pygame.draw.rect(screen, (70, 70, 70), status_box, border_radius=10)
    states = state_controller.get_status()
    satiety_text = font.render(f"Сытость: {int(states['satiety'])}", True, WHITE)
    communication_text = font.render(f"Общение: {int(states['communication'])}", True, WHITE)
    psychological_text = font.render(f"Псих. состояние: {int(states['psychological'])}", True, WHITE)
    mood_text = font.render(f"Настроение: {states['mood']}", True, WHITE)
    screen.blit(satiety_text, (status_box.x + 10, status_box.y + 10))
    screen.blit(communication_text, (status_box.x + 10, status_box.y + 30))
    screen.blit(psychological_text, (status_box.x + 10, status_box.y + 50))
    screen.blit(mood_text, (status_box.x + 10, status_box.y + 70))

    # Отображаем кнопку "Покормить"
    mouse_pos = pygame.mouse.get_pos()
    if feed_button.collidepoint(mouse_pos):
        pygame.draw.rect(screen, BUTTON_HOVER_COLOR, feed_button, border_radius=10)
    else:
        pygame.draw.rect(screen, BUTTON_COLOR, feed_button, border_radius=10)
    feed_text = font.render("Покормить", True, WHITE)
    text_rect = feed_text.get_rect(center=feed_button.center)
    screen.blit(feed_text, text_rect)

    pygame.display.flip()
    clock.tick(30)

    # Отображаем поле ввода
    box_color = INPUT_BOX_COLOR_ACTIVE if input_active else INPUT_BOX_COLOR_INACTIVE
    pygame.draw.rect(screen, box_color, input_box)
    input_surface = font.render(user_text, True, WHITE)
    screen.blit(input_surface, (input_box.x + 5, input_box.y + 5))

    pygame.display.flip()
    clock.tick(30)

pygame.quit()
sys.exit()
