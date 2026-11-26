# V1 Initial Trie prototype
# Naive list search that fails startsWith and empty boundary
class Trie:
    def __init__(self):
        self.words = []

    def insert(self, word: str) -> None:
        self.words.append(word)

    def search(self, word: str) -> bool:
        return word in self.words

    def startsWith(self, prefix: str) -> bool:
        # Flaw: incorrect prefix logic
        return False

