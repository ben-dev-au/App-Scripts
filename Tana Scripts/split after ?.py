# split after colon

# import pyperclip as pc

# text = pc.paste()
# text = text.splitlines()
# newText = ""

# for line in text:
#     pass

# -----

# import pyperclip
# import re


# def split_line(line):
#     """
#     Splits a line at the first colon and formats it with indentation.

#     Parameters:
#         line (str): The input line to process.

#     Returns:
#         str: The formatted line with indentation after the colon.
#     """
#     # Use regex to split at the first colon
#     match = re.match(r"([^:]+):\s*(.*)", line)
#     if match:
#         before_colon = match.group(1).strip()
#         after_colon = match.group(2).strip()
#         return f"{before_colon}:\n    {after_colon}"
#     else:
#         # If no colon is found, return the line as is
#         return line


# def process_text(text):
#     """
#     Processes multiple lines of text, splitting each line at the first colon.

#     Parameters:
#         text (str): The multiline input text.

#     Returns:
#         str: The transformed text with proper formatting.
#     """
#     lines = text.splitlines()
#     new_lines = [split_line(line) for line in lines]
#     return "\n".join(new_lines)


# def main():
#     """
#     Main function to execute the text processing.
#     """
#     try:
#         # Get text from the clipboard
#         text = pyperclip.paste()
#         print("Original Text:")
#         print(text)
#         print("\nProcessing...\n")

#         # Process the text
#         transformed_text = process_text(text)

#         # Copy the transformed text back to the clipboard
#         pyperclip.copy(transformed_text)

#         print("Transformed Text:")
#         print(transformed_text)
#         print("\nThe transformed text has been copied to your clipboard.")

#     except pyperclip.PyperclipException as e:
#         print("Error accessing the clipboard. Make sure it's accessible.")
#         print(e)


# if __name__ == "__main__":
#     main()


# -----

# import pyperclip
# import re


# def split_line(line):
#     """
#     Splits a line at the first colon and returns the title and description.

#     Parameters:
#         line (str): The input line to process.

#     Returns:
#         tuple: A tuple containing the title and description.
#     """
#     # Use regex to split at the first colon
#     match = re.match(r"([^:]+):\s*(.*)", line)
#     if match:
#         title = match.group(1).strip()
#         description = match.group(2).strip()
#         return title, description
#     else:
#         # If no colon is found, return the line as title and empty description
#         return line.strip(), ""


# def process_text_no_duplicates(text):
#     """
#     Processes multiple lines of text to format them with bullets and indentation,
#     avoiding duplicate descriptions.

#     Parameters:
#         text (str): The multiline input text.

#     Returns:
#         str: The transformed text with proper formatting.
#     """

#     lines = text.splitlines()
#     new_lines = ["%%tana%%"]  # Start with %%tana%%

#     for line in lines:
#         if not line.strip():
#             # Skip empty lines
#             continue

#         title, description = split_line(line)

#         if description:
#             # Add a bullet for the title with an indented bullet for the description
#             new_lines.append(f"- {title}:\n  - {description}")
#         else:
#             # If there's no description, just add the title as a bullet
#             new_lines.append(f"- {title}")

#     return "\n".join(new_lines)


# def main():
#     """
#     Main function to execute the text processing.
#     """
#     try:
#         # Get text from the clipboard
#         text = pyperclip.paste()

#         print("Original Text:")
#         print(text)
#         print("\nProcessing...\n")

#         # Process the text without duplicates
#         transformed_text = process_text_no_duplicates(text)

#         # Copy the transformed text back to the clipboard
#         pyperclip.copy(transformed_text)

#         print("Transformed Text:")
#         print(transformed_text)
#         print("\nThe transformed text has been copied to your clipboard.")

#     except pyperclip.PyperclipException as e:
#         print("Error accessing the clipboard. Make sure it's accessible.")
#         print(e)


# if __name__ == "__main__":
#     main()
import pyperclip
import re


def split_paragraphs(line):
    """
    Splits a line after each "?" and returns a list of parts.

    Parameters:
        line (str): The input line to process.

    Returns:
        list: A list of split parts.
    """
    # Use regex to find all substrings ending with "?"
    matches = re.findall(r'[^?]+?\?', line)
    parts = [match.strip() for match in matches]
    
    # Capture any remaining text after the last "?"
    remaining = re.sub(r'[^?]+?\?\s*', '', line).strip()
    if remaining:
        parts.append(remaining)
    
    return parts


def process_text_with_nesting(text):
    """
    Processes multiple lines of text to format them with nested bullets,
    splitting after each "?" and nesting subsequent parts under the first.

    Parameters:
        text (str): The multiline input text.

    Returns:
        str: The transformed text with proper formatting.
    """

    lines = text.splitlines()
    new_lines = ["%%tana%%"]  # Start with %%tana%%

    for line in lines:
        if not line.strip():
            # Skip empty lines
            continue

        parts = split_paragraphs(line)

        if parts:
            # The first part is the main bullet
            main_bullet = f"- {parts[0]}"
            new_lines.append(main_bullet)

            # Subsequent parts are nested bullets
            for part in parts[1:]:
                if part:
                    nested_bullet = f"  - {part}"
                    new_lines.append(nested_bullet)

    return "\n".join(new_lines)


def main():
    """
    Main function to execute the text processing.
    """
    try:
        # Get text from the clipboard
        text = pyperclip.paste()

        print("Original Text:")
        print(text)
        print("\nProcessing...\n")

        # Process the text with nesting
        transformed_text = process_text_with_nesting(text)

        # Copy the transformed text back to the clipboard
        pyperclip.copy(transformed_text)

        print("Transformed Text:")
        print(transformed_text)
        print("\nThe transformed text has been copied to your clipboard.")

    except pyperclip.PyperclipException as e:
        print("Error accessing the clipboard. Make sure it's accessible.")
        print(e)


if __name__ == "__main__":
    main()
