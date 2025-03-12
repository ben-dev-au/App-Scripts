import pyperclip as pc


text = pc.paste()


def MergeLines(text):
    text = text.splitlines()
    mergedText = ""

    for line in text:
        mergedText += line + " "

    mergedText = mergedText.rstrip()

    return mergedText


mergedText = MergeLines(text)
# print(mergedText)
pc.copy(mergedText)
