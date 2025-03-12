#!/opt/homebrew/bin/python3

import re
import pyperclip


def split_on_dash(text, separator="- "):
    """
    Splits the text based on the specified separator, removes the separator,
    and returns a list of cleaned items.
    """
    return [item.strip() for item in text.split(separator) if item.strip()]


def split_sentences(text):
    """
    Splits the text into sentences based on punctuation followed by whitespace
    and a capital letter. Replaces the space with a newline character.
    """
    regex_pattern = r"(?<=[.!?])\s+(?=[A-Z])"
    return re.sub(regex_pattern, "\n", text)


def contains_dash_list(text, separator="- "):
    """
    Detects if the text contains multiple instances of the separator,
    suggesting it's a list that should be split on the separator.
    """
    # Count the number of separator occurrences
    separator_count = text.count(separator)
    # Define a threshold for considering it a list.
    threshold = 2
    return separator_count >= threshold


def normalise_spaces(text):
    """
    Normalise space characters in the text.
    """
    return re.sub(r"\s+", " ", text)
    # return "".join(" " if unicodedata.category(c) == "Zs" else c for c in text)


def main():
    # Step 1: Get the text from the clipboard
    text = pyperclip.paste()
    text = normalise_spaces(text)

    if not text.strip():
        print("Clipboard is empty. Please copy some text and try again.")
        return

    # Step 2: Detect which splitting method to use
    if contains_dash_list(text, separator="- "):
        print("Detected dash-separated list. Applying dash splitting...")
        # Apply dash splitting
        items = split_on_dash(text, separator="- ")
        combined_text = "\n".join(items)
    else:
        print("Dash-separated list not detected. Applying sentence splitting...")
        # Apply sentence splitting
        combined_text = split_sentences(text)

    # Step 3: Copy the updated text back to the clipboard
    pyperclip.copy(combined_text)

    print("The modified text has been copied to your clipboard.")


if __name__ == "__main__":
    main()
