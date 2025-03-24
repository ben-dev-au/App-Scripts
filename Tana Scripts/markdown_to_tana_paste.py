import re
import sys
import pyperclip


class MarkdownToTanaConverter:
    class Node:
        def __init__(self, node_type, content, level=0):
            self.type = node_type  # 'heading', 'bullet', 'numbered', 'text', or 'code'
            self.content = content
            self.level = level
            self.children = []
            self.parent = None

        def add_child(self, child):
            child.parent = self
            self.children.append(child)

        def __repr__(self):
            return f"{self.type}({self.level}): {self.content}"

    def __init__(self, markdown_text):
        self.markdown_text = markdown_text
        self.code_blocks = []
        self.clean_lines = []
        self.root = None
        # Tracks the last heading node (hash or bold)
        self.last_heading = None

    def _extract_code_blocks(self):
        """
        Extract code blocks from the markdown text.
        Fenced code blocks are replaced by placeholders in self.clean_lines.
        """
        lines = self.markdown_text.splitlines()
        in_code_block = False
        code_block_lang = ""
        code_block_content = ""
        for line in lines:
            if line.strip().startswith("```"):
                if in_code_block:
                    # End of code block.
                    in_code_block = False
                    self.code_blocks.append(
                        (code_block_lang, code_block_content.rstrip())
                    )
                    self.clean_lines.append(
                        f"CODE_BLOCK_PLACEHOLDER_{len(self.code_blocks) - 1}"
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
                    self.clean_lines.append(line)

    def _build_tree(self):
        """
        Build the document tree from the clean markdown lines.
        For hash headings, the explicit level is used (based on the number of '#' characters).
        For pure bold headings, the new heading is appended as a child of the current
        container unless the immediately preceding heading was also bold—in that case the new
        bold heading is attached as a sibling (i.e. using the previous heading’s parent).
        List items are attached under the most recent node whose content ends with a colon.
        """
        self.root = self.Node("root", "root", level=0)
        current_node = self.root
        # Keeps track of heading nodes for levels 1-6.
        heading_nodes = {i: None for i in range(1, 7)}
        # Initialize last_heading to root so that if no heading was seen, new ones are
        # attached to the root.
        self.last_heading = self.root

        # current_list_parent is used when the preceding line ends with a colon.
        current_list_parent = None
        # list_stack is used to nest list items based on their leading whitespace.
        list_stack = []

        for line in self.clean_lines:
            if not line.strip():
                continue

            line = line.rstrip()

            # Remove blockquote markers if present.
            if line.lstrip().startswith(">"):
                line = line.lstrip()[1:].lstrip()

            # Check for markdown headings starting with "#".
            heading_match = re.match(r"^(#{1,6})\s+(.+)$", line)
            if heading_match:
                level = len(heading_match.group(1))
                content = heading_match.group(2).strip()
                parent = self.root
                # Find the nearest existing heading at a lower level.
                for i in range(1, level):
                    if heading_nodes.get(i) is not None:
                        parent = heading_nodes[i]
                # Create a heading node using the explicit level.
                node = self.Node("heading", content, level)
                parent.add_child(node)
                heading_nodes[level] = node
                # Clear lower heading nodes.
                for i in range(level + 1, 7):
                    heading_nodes[i] = None

                current_node = node
                self.last_heading = node
                current_list_parent = node if node.content.endswith(":") else None
                continue

            # --- Process pure bold headings ---
            bold_heading_match = re.match(r'^\*\*(.+?)\*\*\s*$', line)
            if bold_heading_match:
                content = bold_heading_match.group(1).strip()
                if self.last_heading is not None and getattr(
                    self.last_heading, "is_bold", False
                ):
                    # If the previous heading was bold, attach as a sibling.
                    parent = self.last_heading.parent or current_node
                else:
                    parent = current_node
                # For bold headings, we assign level = parent's level + 1.
                node = self.Node("heading", content, parent.level + 1)
                # Mark this node as coming from a pure bold line.
                node.is_bold = True
                parent.add_child(node)
                current_node = node
                self.last_heading = node
                current_list_parent = node if node.content.endswith(":") else None
                continue

            # --- Process list items (numbered or bullet) ---
            numbered_match = re.match(r"^(\s*)(\d+\.)\s+(.*)$", line)
            bullet_match = re.match(r"^(\s*)[-*+]\s+(.*)$", line)
            if numbered_match or bullet_match:
                if current_list_parent is None:
                    if (
                        current_node.children
                        and current_node.children[-1].content.endswith(":")
                    ):
                        current_list_parent = current_node.children[-1]
                    elif current_node.content.endswith(":"):
                        current_list_parent = current_node
                    else:
                        current_list_parent = current_node

                if numbered_match:
                    indent = len(numbered_match.group(1))
                    list_type = "numbered"
                    content = numbered_match.group(3).strip()
                else:
                    indent = len(bullet_match.group(1))
                    list_type = "bullet"
                    content = bullet_match.group(2).strip()

                # Determine proper nesting via the list_stack.
                if list_stack:
                    while list_stack and indent <= list_stack[-1][0]:
                        list_stack.pop()
                    if list_stack:
                        parent = list_stack[-1][1]
                    else:
                        parent = current_list_parent
                else:
                    parent = current_list_parent

                node = self.Node(list_type, content, parent.level + 1)
                parent.add_child(node)
                list_stack.append((indent, node))
                # List items do not change the heading context.
                continue

            # --- Process plain text lines ---
            # Clear any active list nesting.
            list_stack = []
            node = self.Node("text", line.strip(), current_node.level + 1)
            current_node.add_child(node)
            current_list_parent = node if node.content.endswith(":") else None

    def _replace_code_blocks(self, node):
        """
        Recursively replace any code block placeholders in the tree with proper code nodes.
        """
        if "CODE_BLOCK_PLACEHOLDER_" in node.content:
            m = re.search(r"CODE_BLOCK_PLACEHOLDER_(\d+)", node.content)
            if m:
                idx = int(m.group(1))
                node.type = "code"
                node.content = ""
                node.code_lang = self.code_blocks[idx][0]
                node.code_content = self.code_blocks[idx][1]
        for child in node.children:
            self._replace_code_blocks(child)

    def _build_tana_structure(self, node, indent=0):
        """
        Recursively build the Tana Paste nested bullet output from the document tree.
        """
        result = []
        indent_str = " " * indent

        if node.type == "code":
            result.append(f"{indent_str}- ```{node.code_lang}")
            for cl in node.code_content.splitlines():
                result.append(f"{indent_str}- {cl}")
            result.append(f"{indent_str}- ```")
        elif node.type != "root":
            if node.type == "heading":
                # For top‐level (hash) headings we use "!!", otherwise we wrap the text in bold markers.
                if node.level == 1:
                    text = f"!! {node.content}"
                else:
                    text = f"**{node.content}**"
            elif node.type in ("bullet", "numbered"):
                text = node.content
            else:
                text = node.content
            result.append(f"{indent_str}- {text}")

        for child in node.children:
            result.extend(self._build_tana_structure(child, indent + 2))
        return result

    def convert(self):
        """
        Run the full conversion process and return the Tana Paste output.
        """
        self._extract_code_blocks()
        self._build_tree()
        self._replace_code_blocks(self.root)
        tana_structure = self._build_tana_structure(self.root)
        tana_output = "%%tana%%\n" + "\n".join(tana_structure)
        return tana_output


markdown_text = pyperclip.paste()
converter = MarkdownToTanaConverter(markdown_text)
result = converter.convert()
print(result)
pyperclip.copy(result)
# pyperclip.paste(result)