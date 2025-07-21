import json
import os

class LongTermMemory:
    def __init__(self, log_file_path="memory/long_memory.json"):
        self.log_file_path = log_file_path
        self.memory = self._load_memory()

    def _load_memory(self):
        if not os.path.exists(self.log_file_path):
            with open(self.log_file_path, "w", encoding="utf-8") as f:
                json.dump([], f)
            return []
        with open(self.log_file_path, "r", encoding="utf-8") as f:
            memory = json.load(f)
        return memory

    def add(self, info):
        entry = {"info": info}
        self.memory.append(entry)
        with open(self.log_file_path, "w", encoding="utf-8") as f:
            json.dump(self.memory, f, ensure_ascii=False, indent=2)

    def get_summary(self):
        return "\\n".join(item["info"] for item in self.memory)
