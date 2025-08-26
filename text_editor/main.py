from dataclasses import dataclass


# Flyweight object
@dataclass(frozen=True)
class Style:
    font_name: str
    font_size: int
    bold: bool
    italic: bool


# Flyweight Factory
class StyleFactory:
    _cache = {}

    @classmethod
    def get_style(cls, font_name, font_size, bold, italic):
        key = (font_name, font_size, bold, italic)
        if key not in cls._cache:
            cls._cache[key] = Style(font_name, font_size, bold, italic)
        return cls._cache[key]


# Character + reference to shared Style
class CharacterCell:
    __slots__ = ('ch', 'style')

    def __init__(self, ch, style):
        self.ch = ch
        self.style = style


# Main document class
class Document:
    def __init__(self):
        self.document = []  # list of rows, each row = list of CharacterCell

    def add_character(self, row, column, ch, font_name, font_size, is_bold, is_italic):
        style = StyleFactory.get_style(font_name, font_size, is_bold, is_italic)

        # expand rows if needed
        while len(self.document) <= row:
            self.document.append([])

        target_row = self.document[row]
        cell = CharacterCell(ch, style)

        # insert at column (shift right) or append
        if column < len(target_row):
            target_row.insert(column, cell)
        else:
            target_row.append(cell)

    def get_style(self, row, col):
        if row < 0 or row >= len(self.document):
            return ""
        target_row = self.document[row]
        if col < 0 or col >= len(target_row):
            return ""
        cell = target_row[col]

        parts = [cell.ch, cell.style.font_name, str(cell.style.font_size)]
        if cell.style.bold:
            parts.append("b")
        if cell.style.italic:
            parts.append("i")
        return "-".join(parts)

    def read_line(self, row):
        if row < 0 or row >= len(self.document):
            return ""
        return "".join(cell.ch for cell in self.document[row])

    def delete_character(self, row, col):
        if row < 0 or row >= len(self.document):
            return False
        target_row = self.document[row]
        if col < 0 or col >= len(target_row):
            return False
        target_row.pop(col)
        return True


if __name__ == "__main__":
    doc = Document()
    doc.add_character(0, 0, 'H', "Arial", 12, True, False)
    doc.add_character(0, 1, 'i', "Arial", 12, True, False)

    print(doc.read_line(0))            # Output: Hi
    print(doc.get_style(0, 1))         # Output: i-Arial-12-b
    doc.delete_character(0, 0)
    print(doc.read_line(0))            # Output: i

