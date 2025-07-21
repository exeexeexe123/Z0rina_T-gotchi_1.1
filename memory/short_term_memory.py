import json
import os

class ShortTermMemory:
    DEFAULT_LIFE = 2

    def __init__(self, max_size=1000, log_file_path="memory/short_memory.json"):
        self.max_size = max_size
        self.log_file_path = log_file_path
        self.memory = self._load_memory()

    def _load_memory(self):
        if not os.path.exists(self.log_file_path):
            with open(self.log_file_path, "w", encoding="utf-8") as f:
                json.dump([], f)
            return []
        with open(self.log_file_path, "r", encoding="utf-8") as f:
            memory = json.load(f)
        # Уменьшаем жизнь каждой реплики на 1, удаляем с жизнью 0
        updated_memory = []
        for item in memory:
            life = item.get("life", self.DEFAULT_LIFE)
            life -= 1
            if life > 0:
                item["life"] = life
                updated_memory.append(item)
        # Сохраняем обновленную память
        with open(self.log_file_path, "w", encoding="utf-8") as f:
            json.dump(updated_memory, f, ensure_ascii=False, indent=2)
        return updated_memory

    def add(self, user_input, bot_response):
        entry = {"user": user_input, "bot": bot_response, "life": self.DEFAULT_LIFE}
        self.memory.append(entry)
        if len(self.memory) > self.max_size:
            self.memory.pop(0)
        self._write_log()

    def get_context(self):
        context = ""
        for exchange in self.memory:
            context += f"Пользователь: {exchange['user']}\nЗорина: {exchange['bot']}\n"
        return context

    def _write_log(self):
        with open(self.log_file_path, "w", encoding="utf-8") as f:
            json.dump(self.memory, f, ensure_ascii=False, indent=2)
