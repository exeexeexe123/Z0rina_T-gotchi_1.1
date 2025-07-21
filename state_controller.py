import time
import json
import os

class Satiety:
    def __init__(self):
        self.value = 100
        self.last_fed_time = time.time()

    def feed(self):
        self.value = min(100, self.value + 30)
        self.last_fed_time = time.time()

    def decay(self, elapsed):
        # Уменьшение на 5 каждые 10 минут
        decrease = (elapsed // 600) * 5
        if decrease > 0:
            self.value = max(0, self.value - decrease)

class Communication:
    def __init__(self):
        self.value = 100
        self.last_communicated_time = time.time()

    def communicate(self):
        self.value = min(100, self.value + 10)
        self.last_communicated_time = time.time()

    def decay(self, elapsed):
        # Уменьшение на 5 каждые 20 минут
        decrease = (elapsed // 1200) * 5
        if decrease > 0:
            self.value = max(0, self.value - decrease)

class PsychologicalState:
    def __init__(self):
        self.value = 100

    def update(self, satiety_value, communication_value, elapsed):
        hunger_factor = max(0, 50 - satiety_value)
        communication_factor = max(0, 50 - communication_value)
        time_factor = elapsed / 3600  # в часах

        if satiety_value > 50 and communication_value > 50:
            increase = 5 * time_factor  # скорость восстановления
            self.value = min(100, self.value + increase)
        else:
            decrease = (hunger_factor + communication_factor) * time_factor * 0.1
            self.value = max(0, self.value - decrease)

class Mood:
    def __init__(self):
        self.state = "спокойствие"

    def update(self, satiety_value, communication_value, psychological_value):
        if psychological_value <= 0:
            self.state = "мертвая"
        elif psychological_value < 50:
            self.state = "депрессия"
        elif satiety_value < 50 and communication_value < 50:
            self.state = "грусть"
        elif communication_value > 50 and satiety_value < 50:
            self.state = "злость"
        elif (satiety_value > 50 and communication_value > 50 and psychological_value > 50 and
              (satiety_value < 100 or communication_value < 100 or psychological_value < 100)):
            self.state = "спокойствие"
        elif satiety_value == 100 and communication_value == 100:
            self.state = "радость"
        else:
            self.state = "спокойствие"

class StateController:
    def __init__(self, save_path="state_data.json"):
        self.save_path = save_path
        self.satiety = Satiety()
        self.communication = Communication()
        self.psychological = PsychologicalState()
        self.mood = Mood()
        self.last_update_time = time.time()
        self.is_dead = False
        self.load_state()

    def load_state(self):
        if os.path.exists(self.save_path):
            try:
                with open(self.save_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.satiety.value = data.get("satiety", 100)
                    self.satiety.last_fed_time = data.get("last_fed_time", time.time())
                    self.communication.value = data.get("communication", 100)
                    self.communication.last_communicated_time = data.get("last_communicated_time", time.time())
                    self.psychological.value = data.get("psychological", 100)
                    self.mood.state = data.get("mood", "спокойствие")
                    self.last_update_time = data.get("last_update_time", time.time())
                    self.is_dead = data.get("is_dead", False)
                    self.update_states()
            except Exception as e:
                print(f"Ошибка загрузки состояния: {e}")

    def save_state(self):
        data = {
            "satiety": self.satiety.value,
            "last_fed_time": self.satiety.last_fed_time,
            "communication": self.communication.value,
            "last_communicated_time": self.communication.last_communicated_time,
            "psychological": self.psychological.value,
            "mood": self.mood.state,
            "last_update_time": self.last_update_time,
            "is_dead": self.is_dead
        }
        try:
            with open(self.save_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"Ошибка сохранения состояния: {e}")

    def update_states(self):
        if self.is_dead:
            return

        current_time = time.time()
        elapsed = current_time - self.last_update_time

        self.satiety.decay(elapsed)
        self.communication.decay(elapsed)
        self.psychological.update(self.satiety.value, self.communication.value, elapsed)
        self.mood.update(self.satiety.value, self.communication.value, self.psychological.value)

        self.last_update_time = current_time
        self.save_state()

        if self.psychological.value <= 0:
            self.is_dead = True

    def feed(self):
        if self.is_dead:
            return "Зорина уже умерла."
        self.update_states()
        self.satiety.feed()
        self.save_state()
        return "Ты покормил Зорину. Сытость увеличена."

    def communicate(self):
        if self.is_dead:
            return "Зорина уже умерла."
        self.update_states()
        self.communication.communicate()
        self.save_state()

    def get_status(self):
        return {
            "satiety": self.satiety.value,
            "communication": self.communication.value,
            "psychological": self.psychological.value,
            "mood": self.mood.state,
            "is_dead": self.is_dead
        }
