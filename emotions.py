class Emotions:
    def __init__(self, gemini_api):
        self.gemini = gemini_api
        self.current_emotion = None
        self.emotion_list = ["радость", "грусть", "злость", "страх", "удивление", "спокойствие"]

    def choose_emotion(self, context_text):
        prompt = (
            f"Вот список эмоций: {', '.join(self.emotion_list)}.\n"
            f"Исходя из контекста: \"{context_text}\", "
            "ответь одним словом, какую эмоцию ты сейчас чувствуешь из этого списка."
        )
        response = self.gemini.generate_content(prompt)
        # Предполагается, что ответ - одно слово из списка эмоций
        content = response.get("candidates", [{}])[0].get("content", {})
        parts = content.get("parts", [])
        emotion = ""
        if parts and isinstance(parts, list):
            emotion = "".join(part.get("text", "") for part in parts).strip().lower()
        if emotion in self.emotion_list:
            self.current_emotion = emotion
        else:
            self.current_emotion = "спокойствие"
        return self.current_emotion

    def get_emotion_context(self):
        if self.current_emotion:
            return f"Сейчас я чувствую {self.current_emotion}."
        return ""
