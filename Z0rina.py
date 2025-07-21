from gemini_api import GeminiAPI
from awareness import Awareness
from state_controller import StateController

def main():
    print("Просыпайся Z0rina...")
    gemini = GeminiAPI()
    awareness = Awareness()
    state_controller = StateController()
    print("Можешь писать...")
    try:
        while True:
            user_input = input("Я: ")
            if user_input.lower() == "бб":
                print("Засыпай...")
                break
            if user_input.lower() == "покормить":
                feed_result = state_controller.feed()
                print(feed_result)
                continue
            try:
                # Проверяем команду памяти через контроллер
                command_result = awareness.memory_controller.process_command(user_input)
                if command_result:
                    print(command_result)
                    continue

                # Обновляем состояние общения
                state_controller.communicate()

                # Формируем контекст с личностью и памятью
                personality = awareness.get_personality_description()
                memory_context = awareness.get_context()

                # Получаем текущую эмоцию из нового контроллера
                emotion = state_controller.mood.state
                emotion_context = f"Текущее настроение Зорины: {emotion}"

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
                    f"Вопрос: {user_input}"
                )
                response = gemini.generate_content(prompt)
                # Предполагается, что ответ содержится в response в определённом поле
                # Нужно адаптировать под реальный формат ответа Gemini API
                content = response.get("candidates", [{}])[0].get("content", {})
                parts = content.get("parts", [])
                answer = ""
                if parts and isinstance(parts, list):
                    answer = "".join(part.get("text", "") for part in parts)
                if not answer:
                    answer = str(response)

                print("\n" + "-"*40)
                print(f"[Эмоция Зорины: {emotion}]")
                print("Z0rina: " + answer)
                print("-"*40 + "\n")
                # Добавляем в память
                awareness.add_to_memory(user_input, answer)
            except Exception as e:
                print(f"Ошибка при вызове Gemini API: {e}")
    except KeyboardInterrupt:
        print("\nТы меня выключил принудительно...")

if __name__ == "__main__":
    main()
