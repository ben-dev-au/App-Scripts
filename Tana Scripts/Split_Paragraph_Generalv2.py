#!/opt/homebrew/bin/python3

import re
import pyperclip

# Define the list of characters/strings to use for splitting.
# Add more characters here as needed.
LIST_SEPARATORS = ["- ", "• "]
MIN_SEPARATOR_COUNT = 2  # Change threshold if desired


def split_on_separators(text, separators):
    """
    Splits the text based on any of the given separators. Returns a list
    of cleaned items with the separators removed.
    """
    # Create a regex pattern that matches any of the separators.
    pattern = "|".join(map(re.escape, separators))
    return [item.strip() for item in re.split(pattern, text) if item.strip()]


def split_sentences(text):
    """
    Splits the text into sentences based on punctuation followed by whitespace
    and a capital letter. Replaces the space with a newline character.
    """
    regex_pattern = r"(?<=[.!?])\s+(?=[A-Z])"
    return re.sub(regex_pattern, "\n", text)


def contains_list_separator(text, separators, threshold=MIN_SEPARATOR_COUNT):
    """
    Checks if the text contains any of the separators at least 'threshold' times.
    """
    return any(text.count(sep) >= threshold for sep in separators)


def normalise_spaces(text):
    """
    Normalise space characters in the text.
    """
    return re.sub(r"\s+", " ", text)


def main():
    # Step 1: Get the text from the clipboard
    text = pyperclip.paste()
    text = normalise_spaces(text)

    if not text.strip():
        print("Clipboard is empty. Please copy some text and try again.")
        return

    # Step 2: Detect which splitting method to use
    if contains_list_separator(text, LIST_SEPARATORS):
        print("Detected list separators. Applying multi-character splitting...")
        # Apply splitting on any of the defined list separators
        items = split_on_separators(text, LIST_SEPARATORS)
        combined_text = "\n".join(items)
    else:
        print("List separators not detected. Applying sentence splitting...")
        # Apply sentence splitting
        combined_text = split_sentences(text)

    # Step 3: Copy the updated text back to the clipboard
    pyperclip.copy(combined_text)
    print("The modified text has been copied to your clipboard.")


if __name__ == "__main__":
    main()
