def analyze_sentence(text: str) -> tuple[int, int, bool]:
    """Return (length, word count, contains 'python') for the given text."""
    length = len(text)
    word_count = len(text.split())
    contains_python = "python" in text.lower()

    return length, word_count, contains_python


if __name__ == "__main__":
    text = input("Enter a sentence: ")
    length, word_count, contains_python = analyze_sentence(text)

    print(f"Characters: {length}")
    print(f"Words: {word_count}")
    print(f"Contains 'Python': {contains_python}")
