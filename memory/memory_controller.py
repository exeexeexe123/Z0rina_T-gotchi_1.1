from memory.short_term_memory import ShortTermMemory
from memory.long_term_memory import LongTermMemory

class MemoryController:
    def __init__(self):
        self.short_term_memory = ShortTermMemory()
        self.long_term_memory = LongTermMemory()

    def add_to_short_term(self, user_input, bot_response):
        self.short_term_memory.add(user_input, bot_response)

    def add_to_long_term(self, info):
        self.long_term_memory.add(info)

    def get_combined_context(self):
        return self.long_term_memory.get_summary() + "\n" + self.short_term_memory.get_context()

    def summarize_and_update_long_term(self):
        # Здесь можно добавить логику для анализа короткосрочной памяти
        # и выделения важных фактов для долгосрочной памяти
        pass

    def process_command(self, command_text):
        # Обработка команд памяти
        if command_text.endswith("Запиши это"):
            info = command_text[:-len("Запиши это")].strip(",. ")
            self.add_to_long_term(info)
            return "Информация добавлена в долгосрочную память."
        return None
