"""Explicit interaction counters used for exploratory developmental studies."""


class DevelopmentCounters:
    def __init__(self):
        self.vocabulary = set()
        self.corrections = 0
        self.demonstrations = 0

    def observe_words(self, text):
        self.vocabulary.update(word.strip(".,!?;:").lower() for word in str(text).split() if word.strip(".,!?;:"))
        return len(self.vocabulary)

    def record_correction(self):
        self.corrections += 1
        return self.corrections

    def record_demonstration(self):
        self.demonstrations += 1
        return self.demonstrations
