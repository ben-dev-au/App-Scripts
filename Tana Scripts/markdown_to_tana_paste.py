import re
import pyperclip

# import sys


class MarkdownToTanaConverter:
    class Node:
        def __init__(self, node_type, content, level=0):
            self.type = node_type  # 'heading', 'bullet', 'numbered', 'text', or 'code'
            self.content = content
            self.level = level
            self.children = []
            self.parent = None
            # Check for a colon at the end, but ignore trailing whitespace
            self.ends_with_colon = content.rstrip().endswith(":")

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
                    self.code_blocks.append((code_block_lang, code_block_content.rstrip()))
                    self.clean_lines.append(f"CODE_BLOCK_PLACEHOLDER_{len(self.code_blocks) - 1}")
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

    def _find_parent_for_list_item(self, indent, list_stack, colon_parents):
        """
        Find the appropriate parent for a list item based on indentation and colon parents.
        """
        # First check if we have a colon parent at the current indentation level
        for colon_indent, colon_node in reversed(colon_parents):
            if indent > colon_indent:
                return colon_node

        # If no colon parent found, use the list stack
        if list_stack:
            while list_stack and indent <= list_stack[-1][0]:
                list_stack.pop()
            if list_stack:
                return list_stack[-1][1]

        return None

    def _build_tree(self):
        """
        Build the document tree from the clean markdown lines.
        """
        self.root = self.Node("root", "root", level=0)
        current_node = self.root
        heading_nodes = {i: None for i in range(1, 7)}
        self.last_heading = self.root

        # Track a stack of colon nodes with their indentation levels
        colon_parents = []  # List of (indent, node) tuples
        # list_stack for normal nesting
        list_stack = []

        for line in self.clean_lines:
            if not line.strip():
                continue

            line = line.rstrip()
            line_indent = len(line) - len(line.lstrip())

            # Remove blockquote markers if present
            if line.lstrip().startswith(">"):
                line = line.lstrip()[1:].lstrip()

            # Check for markdown headings starting with "#"
            heading_match = re.match(r"^(#{1,6})\s+(.+)$", line)
            if heading_match:
                level = len(heading_match.group(1))
                content = heading_match.group(2).strip()

                parent = self.root
                for i in range(1, level):
                    if heading_nodes.get(i) is not None:
                        parent = heading_nodes[i]
                node = self.Node("heading", content, level)
                parent.add_child(node)
                heading_nodes[level] = node
                for i in range(level + 1, 7):
                    heading_nodes[i] = None

                current_node = node
                self.last_heading = node

                # Reset colon and list tracking
                colon_parents = []
                list_stack = []

                # If this heading ends with a colon, track it
                if content.endswith(":"):
                    colon_parents.append((line_indent, node))
                continue

            # Process pure bold headings
            bold_heading_match = re.match(r"^\*\*(.+?)\*\*\s*$", line)
            if bold_heading_match:
                content = bold_heading_match.group(1).strip()
                if self.last_heading is not None and getattr(self.last_heading, "is_bold", False):
                    parent = self.last_heading.parent or current_node
                else:
                    parent = current_node
                node = self.Node("heading", content, parent.level + 1)
                node.is_bold = True
                parent.add_child(node)
                current_node = node
                self.last_heading = node

                # Reset colon and list tracking
                colon_parents = []
                list_stack = []

                # If this heading ends with a colon, track it
                if content.endswith(":"):
                    colon_parents.append((line_indent, node))
                continue

            # Process list items (numbered or bullet)
            numbered_match = re.match(r"^(\s*)(\d+\.)\s+(.*)$", line)
            bullet_match = re.match(r"^(\s*)[-*+]\s+(.*)$", line)
            if numbered_match or bullet_match:
                if numbered_match:
                    indent = len(numbered_match.group(1))
                    list_type = "numbered"
                    content = numbered_match.group(3).strip()
                else:
                    indent = len(bullet_match.group(1))
                    list_type = "bullet"
                    content = bullet_match.group(2).strip()

                # Find parent based on indentation
                parent = None

                # Start with colon parent check
                for colon_indent, colon_node in reversed(colon_parents):
                    if indent > colon_indent:
                        parent = colon_node
                        break

                # If no colon parent, use list stack
                if parent is None and list_stack:
                    # Find the closest parent with less indentation
                    current_list_stack = list_stack.copy()
                    while current_list_stack and indent <= current_list_stack[-1][0]:
                        current_list_stack.pop()
                    if current_list_stack:
                        parent = current_list_stack[-1][1]

                # Default to current node if no parent found
                if parent is None:
                    parent = current_node

                # Create the new node
                node = self.Node(list_type, content, parent.level + 1)
                parent.add_child(node)

                # Update list stack - remove any items at same or greater indentation
                while list_stack and indent <= list_stack[-1][0]:
                    list_stack.pop()
                list_stack.append((indent, node))

                # If this item ends with a colon, add it to colon parents
                if content.endswith(":"):
                    # Remove any colon parents at same or greater indentation
                    colon_parents = [cp for cp in colon_parents if cp[0] < indent]
                    colon_parents.append((indent, node))

                continue

            # Process plain text lines
            # Clear list stack if not indented
            if line_indent == 0:
                list_stack = []

            # Find parent for this text line
            parent = self._find_parent_for_list_item(line_indent, list_stack, colon_parents)

            # Default to current node
            if parent is None:
                parent = current_node

            node = self.Node("text", line.strip(), parent.level + 1)
            parent.add_child(node)

            # If this line ends with a colon, add it to colon parents
            if line.strip().endswith(":"):
                # Remove any colon parents at same or greater indentation
                colon_parents = [cp for cp in colon_parents if cp[0] < line_indent]
                colon_parents.append((line_indent, node))

    def _process_tree_after_building(self, node):
        """
        Post-process the tree to ensure proper nesting of items under colon-ending lines.
        """
        # Process each child
        for child in node.children:
            # Recursively process each child first
            self._process_tree_after_building(child)

            # If this node ends with a colon, ensure its children are properly nested
            if child.ends_with_colon:
                # If this child has any siblings that come after it and have the same parent,
                # check if they should be its children instead based on indentation
                parent = child.parent
                if parent:
                    child_index = parent.children.index(child)
                    # Look at subsequent siblings
                    i = child_index + 1
                    while i < len(parent.children):
                        sibling = parent.children[i]
                        # If the sibling is at the same level and has greater indentation
                        # than expected for this level, it should be a child of the colon node
                        if sibling.level == child.level + 1:
                            # Move this sibling to be a child of the colon node
                            parent.children.pop(i)
                            child.add_child(sibling)
                            # Don't increment i since we removed an element
                        else:
                            i += 1

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

    def _build_tana_structure(self, node, indent=0, parent_colon=False):
        """
        Recursively build the Tana Paste nested bullet output from the document tree.
        Tracks if parent ended with colon to apply extra indentation.
        """
        result = []

        # Apply extra indentation if parent ended with colon
        if parent_colon:
            indent += 2

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
            else:
                text = node.content
            result.append(f"{indent_str}- {text}")

        # Check if this node ends with a colon
        ends_with_colon = node.content.strip().endswith(":")

        # Process children
        for child in node.children:
            # Pass the colon flag to children so they know to indent more
            result.extend(self._build_tana_structure(child, indent + 2, ends_with_colon))

        return result

    def _post_process_tree(self, node):
        """
        Post-process the tree to properly nest items under lines ending with colons.
        """
        i = 0
        while i < len(node.children):
            child = node.children[i]

            # Process child node recursively first
            self._post_process_tree(child)

            # Check if this child ends with a colon
            if child.content.rstrip().endswith(":"):
                # Look ahead at next siblings
                j = i + 1
                while j < len(node.children):
                    next_sibling = node.children[j]
                    # If next sibling is at same level, make it a child of this node
                    if next_sibling.level == child.level:
                        # Move the sibling from parent's children to this child's children
                        node.children.pop(j)
                        next_sibling.level = child.level + 1
                        child.add_child(next_sibling)
                        # Don't increment j since we removed an element
                    else:
                        # Break if we hit something at a different level
                        break
            i += 1

    # Add a call to this in the convert method:
    def convert(self):
        self._extract_code_blocks()
        self._build_tree()
        self._post_process_tree(self.root)
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
