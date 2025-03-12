import re
import pyperclip

# Get the filename from the clipboard
filename = pyperclip.paste()


# Find the last number in the filename and increment it by 1
def increment_last_number(filename):
    matches = list(re.finditer(r"(\d+)", filename))
    if matches:
        last_match = matches[-1]
        number = last_match.group(1)
        new_number = str(int(number) + 1)
        new_filename = filename[: last_match.start()] + new_number + filename[last_match.end() :]
        return new_filename
    return filename


# Generate the new filename
new_filename = increment_last_number(filename)

# Place the new filename back into the clipboard
pyperclip.copy(new_filename)

print(f"Original filename: {filename}")
print(f"New filename: {new_filename}")
