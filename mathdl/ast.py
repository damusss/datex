import enum

class DLSyntaxError(Exception):
    ...

class UnterminatedTextLiteral(DLSyntaxError):
    def __init__(self):
        super().__init__("\" was never closed")

MULTICHARACTER_SYMBOLS = [">=", "<=", "->", "<-", "!="]
BILATERAL_RELATIONAL_OPERATORS = []
UNILATERAL_LEFT_RELATIONAL_OPERATORS = []
UNILATERAL_RIGHT_RELATIONAL_OPERATORS = []
COMMANDS = []

class TK(enum.Enum):
    BILATERAL_RELATIONAL = enum.auto()
    UNILATERAL_LEFT_RELATIONAL = enum.auto()
    UNILATERAL_RIGHT_RELATIONAL = enum.auto()
    TEXT = enum.auto()
    NUMBER = enum.auto()
    SPACE = enum.auto()
    GAP = enum.auto()
    WIDE_GAP = enum.auto()
    SYMBOL = enum.auto()
    COMMAND = enum.auto()
    GROUP_OPEN = enum.auto()
    GROUP_CLOSE = enum.auto()
    VARIABLE = enum.auto()
    FRACTION = enum.auto()
    MULTIPLY = enum.auto()
    SUBSCRIPT = enum.auto()
    SUPERSCRIPT = enum.auto()
    OPTIONAL_DIVIDER = enum.auto()
    EOF = enum.auto()

class Token:
    def __init__(self, kind: TokenKind, value: str = ""):
        self.kind = kind
        self.value = value

class Lexer:
    def __init__(self, source: str):
        self.source = source
        self.eof = False
        self.tokens = []
        if self.source == "":
            self.eof = True
        else:
            self.pos = 0
            self.char = self.source[0]
            self.prev = None

    def advance(self):
        self.prev = self.char
        self.pos += 1
        if len(self.source) <= self.pos:
            self.eof = True
            self.char = None
        else:
            self.char = self.source[self.pos]
        return not self.eof

    def add(self, kind: TK, value: str = ""):
        self.tokens.append(Token(kind, value))

    def add_advance(self, kind: TK, value: str = ""):
        self.add(kind, value)
        return self.advance()

    def get_tokens(self) -> list[str]:
        escaped = False
        spaced = False
        while not self.eof:
            just_spaced = False
            just_escaped = False
            if self.char == "\n":
                while self.char in "\n\t ":
                    self.advance()
            elif escaped and self.char == "t":
                self.add(TK.WIDE_GAP)
            elif self.char == " ":
                if self.advance() and self.char == " ":
                    while self.char in "\t\n ":
                        self.advance()
                    self.add(TK.GAP)
                else:
                    self.add(TK.SPACE)
                just_spaced = True
            elif self.char.isdecimal():
                num = self.char
                while self.advance() and (self.char == "." or self.char.isdecimal()):
                    num += self.char
                self.add(TK.NUMBER, num)
            elif self.char == "`" and not escaped:
                self.advance()
            elif self.char == "*" and not escaped:
                self.add_advance(TK.MULTIPLY)
            elif self.char == "/" and not escaped:
                self.add_advance(TK.FRACTION)
            elif self.char == "@" and not escaped:
                self.add_advance(TK.OPTIONAL_DIVIDER)
            elif self.char == "{" and not escaped:
                self.add_advance(TK.GROUP_OPEN)
            elif self.char == "}" and not escaped:
                self.add_advance(TK.GROUP_CLOSE)
            elif self.char == "_" and not escaped:
                self.add_advance(TK.SUBSCRIPT)
            elif self.char == "^" and not escaped:
                self.add_advance(TK.SUPERSCRIPT)
            elif self.char == "\\" and not escaped:
                just_escaped = True
                self.advance()
            escaped = just_escaped
            spaced = just_spaced
        self.add(TK.EOF)
        return self.tokens

class AST:
    ...

def get_ast(source: str) -> AST:
    return AST()