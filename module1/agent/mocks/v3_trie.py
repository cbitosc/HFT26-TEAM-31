from typing import Dict, Optional


class TrieNode:
    """Node in the production Trie prefix tree."""

    def __init__(self) -> None:
        self.children: Dict[str, TrieNode] = {}
        self.is_end_of_word: bool = False


class Trie:
    """Production-grade Trie data structure supporting insert, search, prefix matching, and word count.

    Attributes:
        root: The root TrieNode instance.
    """

    def __init__(self) -> None:
        """Initializes empty Trie."""
        self.root: TrieNode = TrieNode()
        self._count: int = 0

    def insert(self, word: str) -> None:
        """Inserts a word into the Trie with input safety."""
        if word is None:
            return
        curr = self.root
        for ch in str(word):
            if ch not in curr.children:
                curr.children[ch] = TrieNode()
            curr = curr.children[ch]
        if not curr.is_end_of_word:
            curr.is_end_of_word = True
            self._count += 1

    def search(self, word: str) -> bool:
        """Returns True if the word is in the trie."""
        if word is None:
            return False
        curr = self.root
        for ch in str(word):
            if ch not in curr.children:
                return False
            curr = curr.children[ch]
        return curr.is_end_of_word

    def startsWith(self, prefix: str) -> bool:
        """Returns True if there is any word in the trie that starts with the given prefix."""
        if prefix is None:
            return False
        curr = self.root
        for ch in str(prefix):
            if ch not in curr.children:
                return False
            curr = curr.children[ch]
        return True

    def count(self) -> int:
        """Returns total distinct words currently stored in the Trie."""
        return self._count
