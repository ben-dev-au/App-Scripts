# Copy selected, Add Numbers to the paragraphs and paste.

# import pyperclip as pc

# text = pc.paste()

# class AddNumbersToParagraphs:
#     def __init__(self, text):
#         self.text = text.splitlines()
#         self.newText = ""

#     def AddNumbers(self):
#         for i, line in enumerate(self.text):
#             self.newText += f"{i+1}. {line}\n"

#         return self.newText

#     def __str__(self):
#         return self.newText

# # Add text to clipboard
# pc.copy(AddNumbersToParagraphs(text).AddNumbers())

# # paste the text
# pc.paste()


import pyperclip as pc

def add_numbers_to_paragraphs(text):
    lines = text.splitlines()
    new_text = "%%tana%%\n"
    for i, line in enumerate(lines, start=1):
        new_text += f"- {i}. {line}\n"
    return new_text

def main():
    # Retrieve text from clipboard
    text = pc.paste()
    
    if not text:
        print("Clipboard is empty. Please copy some text and try again.")
        return
    
    # Process the text
    modified_text = add_numbers_to_paragraphs(text)
    
    # Copy the modified text back to clipboard
    pc.copy(modified_text)
    
    # Paste the modified text
    pc.paste()

    # Provide feedback to the user
    # print("Modified text has been copied to the clipboard:")
    # print(modified_text)

if __name__ == "__main__":
    main()


