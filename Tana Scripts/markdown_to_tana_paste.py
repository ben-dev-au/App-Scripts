import re
import sys
import pyperclip

markdown_text = pyperclip.paste()

def markdown_to_tana(markdown_text):
    """
    Convert markdown text to Tana Paste format.

    This function builds a document tree from markdown lines and handles:
        - Extraction of code blocks (so that their content isn't otherwise parsed).
        - Markdown headings (lines starting with "#") and also lines that are entirely bold,
        which are treated as subheadings.
        - Blockquote lines (removing the ">" marker) so that, for example,
        "> **Decompose based on volatility**" is processed as a heading.
        - Bullet lines and regular text lines.
        - Code blocks output as a sequence of bullet items.
    """
    tana_output = "%%tana%%\n"
    lines = markdown_text.splitlines()

    # Extract code blocks first.
    code_blocks = []
    clean_lines = []
    in_code_block = False
    code_block_lang = ""
    code_block_content = ""

    for line in lines:
        if line.strip().startswith("```"):
            if in_code_block:
                # End of code block.
                in_code_block = False
                code_blocks.append((code_block_lang, code_block_content.rstrip()))
                clean_lines.append(
                    f"CODE_BLOCK_PLACEHOLDER_{len(code_blocks) - 1}"
                )
                code_block_content = ""
                code_block_lang = ""
            else:
                # Start of code block.
                in_code_block = True
                code_block_lang = line.strip()[3:].strip()
        else:
            if in_code_block:
                code_block_content += line + "\n"
            else:
                clean_lines.append(line)

    # Define a simple Node class for the document tree.
    class Node:
        def __init__(self, type, content, level=0):
            self.type = type  # 'heading', 'bullet', 'text', or 'code'
            self.content = content
            self.level = level
            self.children = []
            self.parent = None

        def add_child(self, child):
            child.parent = self
            self.children.append(child)

        def __repr__(self):
            return f"{self.type}({self.level}): {self.content}"

    root = Node("root", "root")
    current_node = root
    # To track the last heading node at each level for standard markdown headings.
    heading_nodes = {i: None for i in range(1, 7)}

    # Process each line to build the tree.
    for line in clean_lines:
        if not line.strip():
            continue

        line = line.rstrip()

        # Remove blockquote marker if present.
        if line.lstrip().startswith(">"):
            line = line.lstrip()[1:].lstrip()

        # Check for standard markdown headings (lines starting with "#").
        heading_match = re.match(r"^(#{1,6})\s+(.+)$", line)
        if heading_match:
            level = len(heading_match.group(1))
            content = heading_match.group(2).strip()
            parent = root
            for i in range(1, level):
                if heading_nodes.get(i) is not None:
                    parent = heading_nodes[i]
            node = Node("heading", content, level)
            parent.add_child(node)
            heading_nodes[level] = node
            for i in range(level + 1, 7):
                heading_nodes[i] = None
            current_node = node
            continue

        # Check for bullet lines.
        if re.match(r"^\s*[-*+]\s+", line):
            content = re.sub(r"^\s*[-*+]\s+", "", line).strip()
            node = Node("bullet", content, current_node.level + 1)
            current_node.add_child(node)
            continue

        # Check for a pure bold line.
        bold_heading_match = re.match(r'^\*\*(.+?)\*\*\s*$', line)
        if bold_heading_match:
            content = bold_heading_match.group(1).strip()
            node = Node("heading", content, current_node.level + 1)
            current_node.add_child(node)
            current_node = node
            continue

        # Otherwise, treat the line as plain text.
        node = Node("text", line.strip(), current_node.level + 1)
        current_node.add_child(node)

    # Replace code block placeholders with code nodes.
    def replace_code_blocks(node):
        if "CODE_BLOCK_PLACEHOLDER_" in node.content:
            m = re.search(r"CODE_BLOCK_PLACEHOLDER_(\d+)", node.content)
            if m:
                idx = int(m.group(1))
                node.type = "code"
                node.content = ""
                node.code_lang = code_blocks[idx][0]
                node.code_content = code_blocks[idx][1]
        for child in node.children:
            replace_code_blocks(child)

    replace_code_blocks(root)

    # Convert the tree to the Tana nested bullet format.
    def build_tana_structure(node, indent=0):
        result = []
        indent_str = " " * indent
        if node.type == "code":
            # Output code blocks as bullet items.
            result.append(f"{indent_str}- ```{node.code_lang}")
            for cl in node.code_content.splitlines():
                # Each line in the code block is its own bullet.
                result.append(f"{indent_str}- {cl}")
            result.append(f"{indent_str}- ```")
        elif node.type != "root":
            if node.type == "heading":
                if node.level == 1:
                    text = f"!! {node.content}"
                else:
                    text = f"**{node.content}**"
            else:
                text = node.content
            result.append(f"{indent_str}- {text}")
        for child in node.children:
            result.extend(build_tana_structure(child, indent + 2))
        return result

    tana_structure = build_tana_structure(root)
    tana_output += "\n".join(tana_structure)
    return tana_output


result = markdown_to_tana(markdown_text)
pyperclip.copy(result)
print(result)
