import os
import enum
import json
import string

from . import commands
from .errors import (
    UnterminatedTextLiteral,
    TooManyOptionalParams,
    UnexpectedNode,
    TooManySubSuperScripts,
    UnrecognizedAccent,
)


class OpKind(enum.Enum):
    SYMBOL = enum.auto()
    COMMAND = enum.auto()
    TEXT_SYMBOL = enum.auto()


class OpRelationalBehavior(enum.Enum):
    REGULAR = enum.auto()
    BILATERAL = enum.auto()
    UNILATERAL_LEFT = enum.auto()
    UNILATERAL_RIGHT = enum.auto()


class OpDescriptor:
    def __init__(
        self,
        kind: OpKind,
        value: str,
        relational_behavior: OpRelationalBehavior = OpRelationalBehavior.REGULAR,
        multicharacter_symbol: bool = False,
        aliases=None,
        optional_count=0,
        mandatory_count=0,
        latex="",
        relational_space_count=1,
        command_func=None,
        collect_arguments_until=None,
    ):
        self.kind = kind
        self.value = value
        self.relational_behavior = relational_behavior
        self.multicharacter_symbol = multicharacter_symbol
        if aliases is None:
            aliases = []
        self.aliases = aliases
        self.optional_count = optional_count
        self.mandatory_count = mandatory_count
        self.latex = latex
        self.relational_space_count = relational_space_count
        self.command_func = command_func
        self.collect_arguments_until = collect_arguments_until


IGNORE_SPACES = "\n\t "
IDENTIFIER_LETTERS = string.ascii_lowercase + string.ascii_uppercase
CLOSING_PARENS = ")]}>|"
OPENING_PARENS = "([{<|"

DATEX_PATH = os.path.dirname(os.path.abspath(__file__)) + "/"
OP_DESCRIPTORS_PATH = DATEX_PATH + "op_descriptors/"

STR_TO_RELATIONAL = {
    None: OpRelationalBehavior.REGULAR,
    "r": OpRelationalBehavior.REGULAR,
    "b": OpRelationalBehavior.BILATERAL,
    "ul": OpRelationalBehavior.UNILATERAL_LEFT,
    "ur": OpRelationalBehavior.UNILATERAL_RIGHT,
}

OPERATOR_DESCRIPTORS = []


def load_symbol_operator_descriptor(file_path, multicharacter, kind: OpKind):
    with open(file_path, "r") as fp:
        data = json.load(fp)
        for entry in data:
            value = entry[0]
            if len(entry) > 1:
                relational = STR_TO_RELATIONAL[entry[1]]
            else:
                relational = OpRelationalBehavior.REGULAR
            if len(entry) > 2:
                latex = entry[2]
            else:
                latex = ""
            if len(entry) > 3:
                aliases = entry[3]
            else:
                aliases = None
            if len(entry) > 4:
                space = entry[4]
            else:
                space = 1
            OPERATOR_DESCRIPTORS.append(
                OpDescriptor(
                    kind,
                    value,
                    relational,
                    multicharacter,
                    aliases,
                    0,
                    0,
                    latex,
                    space,
                    None,
                )
            )


def load_command_operator_descriptor(file_path):
    with open(file_path, "r") as fp:
        data = json.load(fp)
        for entry in data:
            value = entry[0]
            args = entry[1]
            collect_until = None
            if isinstance(args, int):
                optional = 0
                mandatory = args
            else:
                optional, mandatory = args
                if isinstance(optional, str):
                    collect_until = optional
                    optional = 0
            if len(entry) > 2:
                aliases = entry[2]
            else:
                aliases = None
            command_func = getattr(commands, value)
            OPERATOR_DESCRIPTORS.append(
                OpDescriptor(
                    OpKind.COMMAND,
                    value,
                    OpRelationalBehavior.REGULAR,
                    False,
                    aliases,
                    optional,
                    mandatory,
                    "",
                    1,
                    command_func,
                    collect_until,
                )
            )


for file in os.listdir(OP_DESCRIPTORS_PATH + "symbols"):
    load_symbol_operator_descriptor(
        OP_DESCRIPTORS_PATH + "symbols/" + file, False, OpKind.SYMBOL
    )

for file in os.listdir(OP_DESCRIPTORS_PATH + "multicharacter_symbols"):
    load_symbol_operator_descriptor(
        OP_DESCRIPTORS_PATH + "multicharacter_symbols/" + file, True, OpKind.SYMBOL
    )

for file in os.listdir(OP_DESCRIPTORS_PATH + "text_symbols"):
    load_symbol_operator_descriptor(
        OP_DESCRIPTORS_PATH + "text_symbols/" + file, True, OpKind.TEXT_SYMBOL
    )

for file in os.listdir(OP_DESCRIPTORS_PATH + "commands/"):
    load_command_operator_descriptor(OP_DESCRIPTORS_PATH + "commands/" + file)


class TK(enum.Enum):
    TEXT = enum.auto()
    NUMBER = enum.auto()
    SPACE = enum.auto()
    SYMBOL = enum.auto()
    TEXT_SYMBOL = enum.auto()
    COMMAND = enum.auto()
    NAME = enum.auto()
    GROUP_OPEN = enum.auto()
    GROUP_CLOSE = enum.auto()
    VARIABLE = enum.auto()
    FRACTION = enum.auto()
    BINOMIAL = enum.auto()
    SUBSCRIPT = enum.auto()
    SUPERSCRIPT = enum.auto()
    ACCENT = enum.auto()
    OPTIONAL_DIVIDER = enum.auto()
    NEWLINE_DIVIDER = enum.auto()
    EOF = enum.auto()


RELATIONAL_TOKENS = [
    TK.TEXT_SYMBOL,
    TK.COMMAND,
    TK.NAME,
    TK.NUMBER,
    TK.VARIABLE,
]


class Token:
    def __init__(self, kind: TK, value=""):
        self.kind = kind
        self.value = value

    def __str__(self):
        if self.value == "":
            return f"{self.kind.name}"
        return f"{self.kind.name} {self.value}"

    __repr__ = __str__

    def render(self):
        if self.kind == TK.EOF:
            return ""
        elif self.kind == TK.SPACE:
            return " " * abs(self.value)
        elif self.kind == TK.GROUP_OPEN:
            return "{"
        elif self.kind == TK.GROUP_CLOSE:
            return "}"
        elif self.kind == TK.OPTIONAL_DIVIDER:
            return "@"
        elif self.kind == TK.FRACTION:
            return "/"
        elif self.kind == TK.BINOMIAL:
            return "/|"
        elif self.kind == TK.SUBSCRIPT:
            return "_"
        elif self.kind == TK.SUPERSCRIPT:
            return "^"
        return str(self.value)


class Lexer:
    def __init__(self, source: str):
        self.source = source
        self.eof = False
        self.tokens: list[Token] = []
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

    def add(self, kind: TK, value=""):
        self.tokens.append(Token(kind, value))

    def add_advance(self, kind: TK, value=""):
        self.add(kind, value)
        return self.advance()

    def add_relational(self, kind: TK, value):
        relational = OpRelationalBehavior.REGULAR
        rel_count = 1
        for op in OPERATOR_DESCRIPTORS:
            if op.value == value:
                relational = op.relational_behavior
                rel_count = op.relational_space_count
                break
        if (
            relational
            in [
                OpRelationalBehavior.BILATERAL,
                OpRelationalBehavior.UNILATERAL_LEFT,
            ]
            and len(self.tokens) > 0
        ):
            if self.tokens[-1].kind in RELATIONAL_TOKENS + [TK.GROUP_CLOSE] or (
                self.tokens[-1].kind == TK.SYMBOL
                and self.tokens[-1].value in CLOSING_PARENS
            ):
                self.add(TK.SPACE, -rel_count)
        self.add(kind, value)

    def get_tokens(self) -> list[Token]:
        if self.source == "":
            return []
        escaped = False
        while not self.eof:
            just_escaped = False
            if self.char in IGNORE_SPACES:
                while self.advance() and self.char in IGNORE_SPACES:
                    ...
            elif self.char == "`" and not escaped:
                count = 1
                while self.advance() and self.char == "`":
                    count += 1
                self.add(TK.SPACE, count)
            elif self.char.isdecimal():
                num = self.char
                while self.advance() and (self.char == "." or self.char.isdecimal()):
                    num += self.char
                self.add(TK.NUMBER, num)
            elif self.char in IDENTIFIER_LETTERS:
                identifier = self.char
                while self.advance() and self.char in IDENTIFIER_LETTERS:
                    identifier += self.char
                if identifier == "row":
                    self.add(TK.NEWLINE_DIVIDER)
                elif len(identifier) == 1:
                    self.add(TK.VARIABLE, identifier)
                else:
                    for op in OPERATOR_DESCRIPTORS:
                        if identifier in op.aliases:
                            identifier = op.value
                            break
                    kind = TK.NAME
                    for op in OPERATOR_DESCRIPTORS:
                        if op.value == identifier:
                            if op.kind == OpKind.COMMAND:
                                kind = TK.COMMAND
                            elif op.kind == OpKind.TEXT_SYMBOL:
                                kind = TK.TEXT_SYMBOL
                    if kind == TK.NAME:
                        if len(self.tokens) > 0 and self.tokens[-1].kind not in [
                            TK.SUBSCRIPT,
                            TK.SUPERSCRIPT,
                            TK.FRACTION,
                            TK.BINOMIAL,
                            TK.OPTIONAL_DIVIDER,
                        ]:
                            self.add(TK.SPACE, -1)
                        self.add(kind, identifier)
                        if self.char not in ["^", "_", "/"]:
                            self.add(TK.SPACE, -1)
                    else:
                        self.add_relational(kind, identifier)
            elif self.char == '"' and not escaped:
                text = ""
                quote_escape = False
                while True:
                    just_quote_escaped = False
                    if not self.advance():
                        raise UnterminatedTextLiteral()
                    if self.char == "\\" and not quote_escape:
                        just_quote_escaped = True
                    elif self.char == '"' and not quote_escape:
                        self.advance()
                        break
                    else:
                        text += self.char
                    quote_escape = just_quote_escaped
                self.add(TK.TEXT, text)
            elif self.char == "*" and not escaped:
                self.add_relational(TK.TEXT_SYMBOL, "dot")
                self.advance()
            elif self.char == "/" and not escaped:
                if self.advance():
                    if self.char == "/":
                        self.add_advance(TK.NEWLINE_DIVIDER)
                    elif self.char == "|":
                        self.add_advance(TK.BINOMIAL)
                    else:
                        self.add(TK.FRACTION)
                else:
                    self.add(TK.FRACTION)
            elif self.char == "@" and not escaped:
                self.add_advance(TK.OPTIONAL_DIVIDER)
            elif self.char == "{" and not escaped:
                self.add_advance(TK.GROUP_OPEN)
            elif self.char == "}" and not escaped:
                self.add_advance(TK.GROUP_CLOSE)
            elif self.char == "_" and not escaped:
                self.add_advance(TK.SUBSCRIPT)
            elif self.char == "^" and not escaped:
                if self.advance() and self.char == "^":
                    self.add_advance(TK.ACCENT)
                else:
                    self.add(TK.SUPERSCRIPT)
            elif self.char == "\\" and not escaped:
                just_escaped = True
                self.advance()
            else:
                value = self.char
                self.advance()
                for op in OPERATOR_DESCRIPTORS:
                    if (
                        op.multicharacter_symbol
                        and len(op.value) == 3
                        and op.value.startswith(value)
                    ):
                        if (
                            self.pos + 1 < len(self.source)
                            and self.char == op.value[1]
                            and self.source[self.pos + 1] == op.value[2]
                        ):
                            value += self.char
                            self.advance()
                            value += self.char
                            self.advance()
                            break
                if len(value) == 1:
                    for op in OPERATOR_DESCRIPTORS:
                        if (
                            len(op.value) == 2
                            and op.multicharacter_symbol
                            and op.value.startswith(value)
                        ):
                            if self.char == op.value[1]:
                                value += self.char
                                self.advance()
                                break
                self.add_relational(TK.SYMBOL, value)
            if (
                len(self.tokens) > 1
                and (
                    self.tokens[-1].kind in RELATIONAL_TOKENS + [TK.GROUP_OPEN]
                    or (
                        self.tokens[-1].kind == TK.SYMBOL
                        and self.tokens[-1].value in OPENING_PARENS
                    )
                )
                and self.tokens[-1].kind != TK.NAME
                and self.tokens[-2].kind in [TK.SYMBOL, TK.COMMAND, TK.TEXT_SYMBOL]
            ):
                for op in OPERATOR_DESCRIPTORS:
                    if op.value == self.tokens[-2].value and op.relational_behavior in [
                        OpRelationalBehavior.BILATERAL,
                        OpRelationalBehavior.UNILATERAL_RIGHT,
                    ]:
                        self.tokens.insert(
                            -1, Token(TK.SPACE, -op.relational_space_count)
                        )
                        break
            escaped = just_escaped
        self.add(TK.EOF)
        return self.tokens


class ASTNode:
    def __str__(self):
        return "Error"

    __repr__ = __str__

    def get_latex(self) -> str:
        return "\\ERROR"


class VoidNode(ASTNode):
    def __str__(self):
        return "Void"

    __repr__ = __str__

    def get_latex(self) -> str:
        return ""


class GroupNode(ASTNode):
    def __init__(self, nodes):
        self.nodes: list[ASTNode] = nodes

    def __str__(self):
        return f"Group({', '.join([str(n) for n in self.nodes])})"

    __repr__ = __str__

    def get_latex(self, bare=False) -> str:
        if bare:
            return " ".join(map(lambda n: n.get_latex(), self.nodes))
        return "{" + self.get_latex(True) + "}"


class UnitNode(ASTNode):
    def __init__(self, tok):
        self.tok: Token = tok

    def __str__(self):
        return f"Unit({self.tok.render()})"

    __repr__ = __str__

    def get_latex(self, bare_symbol=False) -> str:
        if self.tok.kind == TK.SPACE:
            count = abs(self.tok.value)
            if count < 3:
                return "\\," * count
            else:
                return "\\quad"
        elif self.tok.kind == TK.NUMBER or self.tok.kind == TK.VARIABLE:
            return "{" + self.tok.render() + "}"
        elif self.tok.kind == TK.TEXT or self.tok.kind == TK.NAME:
            return "{\\text{" + self.tok.render() + "}}"
        elif self.tok.kind == TK.SYMBOL or self.tok.kind == TK.TEXT_SYMBOL:
            op = None
            for descr in OPERATOR_DESCRIPTORS:
                if descr.value == self.tok.value:
                    op = descr
                    break
            if op is None:
                return self.tok.render()
            else:
                latex = op.latex
                if not isinstance(latex, str):
                    if latex[1] == "bare":
                        bare_symbol = True
                    latex = latex[0]
                if latex == "":
                    result = self.tok.render()
                elif latex == "\\":
                    result = f"\\{self.tok.render()}"
                else:
                    result = latex
                if bare_symbol:
                    return result
                return "{" + result + "}"
        else:
            raise NotImplementedError


class BinaryNode(ASTNode):
    def __init__(self, a_node, b_node, op_tok):
        self.a_node: ASTNode = a_node
        self.b_node: ASTNode = b_node
        self.op_tok: Token = op_tok

    def __str__(self):
        return f"Binary({self.a_node} {self.op_tok.render()} {self.b_node})"

    __repr__ = __str__

    def get_latex(self) -> str:
        if self.op_tok.kind in [TK.FRACTION, TK.BINOMIAL]:
            command = "frac" if self.op_tok.kind == TK.FRACTION else "binom"
            return (
                "{"
                + f"\\{command}"
                + "{"
                + self.a_node.get_latex()
                + "}"
                + "{"
                + self.b_node.get_latex()
                + "}}"
            )
        else:
            raise NotImplementedError


class SubSuperAccentScriptNode(ASTNode):
    def __init__(self, node, subscript_node, superscript_node, accent_node):
        self.node: ASTNode = node
        self.superscript_node: ASTNode | None = superscript_node
        self.subscript_node: ASTNode | None = subscript_node
        self.accent_node: ASTNode | None = accent_node

    def __str__(self):
        return f"({self.node}: Accent[{self.accent_node}] Subscript[{self.subscript_node}] Superscript[{self.superscript_node}])"

    __repr__ = __str__

    def get_accent(self):
        if isinstance(self.accent_node, UnitNode):
            value = self.accent_node.tok.value
            if self.accent_node.tok.kind == TK.SYMBOL:
                if value == "-":
                    return "bar"
                elif value == "->":
                    return "vec"
                elif value == "*":
                    return "dot"
                elif value == "~":
                    return "tilde"
                elif value == "^":
                    return "hat"
                elif value == "-->":
                    return "overrightarrow"
                elif value == "<--":
                    return "overleftarrow"
                elif value == "<->":
                    return "overleftrightarrow"
                else:
                    raise UnrecognizedAccent(value)
            elif self.accent_node.tok.kind == TK.TEXT_SYMBOL:
                if value in [
                    "acute",
                    "grave",
                    "hat",
                    "tilde",
                    "dot",
                    "ddot",
                    "dddot",
                    "vec",
                    "bar",
                    "breve",
                    "widetilde",
                    "widehat",
                    "overbrace",
                    "underbrace",
                    "underline",
                    "overline",
                    "underrightarrow",
                    "underleftarrow",
                    "underleftrightarrow",
                ]:
                    return value
                elif value == "ring":
                    return "mathring"
                else:
                    raise UnrecognizedAccent(value)
            elif self.accent_node.tok.kind == TK.VARIABLE:
                if value == "o":
                    return "ring"
                else:
                    raise UnrecognizedAccent(value)
            else:
                raise UnrecognizedAccent(value)
        else:
            raise UnrecognizedAccent(self.accent_node.get_latex())

    def get_latex(self) -> str:
        latex = "{"
        if isinstance(self.node, UnitNode) and self.node.tok.value in [
            "rightarrow",
            "leftarrow",
        ]:
            latex += f"\\x{self.node.tok.value}"
            if self.subscript_node is not None:
                latex += f"[{self.subscript_node.get_latex()}]"
            if self.superscript_node is not None:
                latex += "{" + self.superscript_node.get_latex() + "}"
            else:
                latex += "{}"
            latex += "}"
            if self.accent_node is None:
                return latex
            else:
                accent = self.get_accent()
                return f"\\{accent}" + "{" + latex + "}"
        if self.accent_node is None:
            latex += self.node.get_latex()
        else:
            accent = self.get_accent()
            latex += "{" + f"\\{accent}" + "{" + self.node.get_latex() + "}}"
        if self.subscript_node is not None:
            if (
                isinstance(self.subscript_node, GroupNode)
                and len(self.subscript_node.nodes) > 0
            ):
                first_node = self.subscript_node.nodes[0]
                if (
                    isinstance(first_node, UnitNode)
                    and first_node.tok.value == "limstyle"
                ):
                    latex += "\\limits"
                elif (
                    isinstance(first_node, UnitNode)
                    and first_node.tok.value == "sidestyle"
                ):
                    latex += "\\nolimits"
            latex += "_" + self.subscript_node.get_latex()
        if self.superscript_node is not None:
            if (
                isinstance(self.superscript_node, GroupNode)
                and len(self.superscript_node.nodes) > 0
            ):
                first_node = self.superscript_node.nodes[0]
                if (
                    isinstance(first_node, UnitNode)
                    and first_node.tok.value == "limstyle"
                ):
                    latex += "\\limits"
                elif (
                    isinstance(first_node, UnitNode)
                    and first_node.tok.value == "sidestyle"
                ):
                    latex += "\\nolimits"
            latex += "^" + self.superscript_node.get_latex()
        return latex + "}"


class CommandNode(ASTNode):
    def __init__(self, command_tok, optional, mandatory):
        self.command_tok: Token = command_tok
        self.optional: list[ASTNode] = optional
        self.mandatory: list[ASTNode] = mandatory

    def __str__(self):
        return f"Command({self.command_tok.render()}, Optional[{', '.join(map(str, self.optional))}], Args[{', '.join(map(str, self.mandatory))}])"

    __repr__ = __str__

    def get_latex(self) -> str:
        op = None
        for descr in OPERATOR_DESCRIPTORS:
            if descr.value == self.command_tok.value:
                op = descr
                break
        return op.command_func(self.optional, self.mandatory)


class Parser:
    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
        self.tokens[-1] = Token(TK.GROUP_CLOSE)
        self.index = 0
        self.tok: Token = self.tokens[0]

    def advance(self):
        self.index += 1
        if self.index >= len(self.tokens):
            self.tok = None
        else:
            self.tok = self.tokens[self.index]

    def parse_command(self, command_tok: Token):
        descr = None
        for op in OPERATOR_DESCRIPTORS:
            if op.value == command_tok.value:
                descr = op
                break
        optional = []
        mandatory = []
        while self.tok.kind == TK.OPTIONAL_DIVIDER:
            self.advance()
            arg = self.parse_binary()
            optional.append(arg)
        if len(optional) > descr.optional_count:
            raise TooManyOptionalParams(command_tok)
        for i in range(descr.mandatory_count):
            arg = self.parse_binary()
            mandatory.append(arg)
        if descr.collect_arguments_until is not None:
            end = False
            while not end:
                nodes = []
                while self.tok.kind != TK.NEWLINE_DIVIDER and not (
                    self.tok.kind == TK.TEXT_SYMBOL
                    and self.tok.value == descr.collect_arguments_until
                ):
                    node = self.parse_binary()
                    nodes.append(node)
                if (
                    self.tok.kind == TK.TEXT_SYMBOL
                    and self.tok.value == descr.collect_arguments_until
                ):
                    end = True
                self.advance()
                optional.append(GroupNode(nodes))
        return CommandNode(command_tok, optional, mandatory)

    def parse_node(self, allow_subsuper=True):
        cur = self.tok
        self.advance()
        node = None
        if cur.kind == TK.GROUP_OPEN:
            node = self.parse_group()
        elif cur.kind in [
            TK.NUMBER,
            TK.TEXT,
            TK.NAME,
            TK.TEXT_SYMBOL,
            TK.SPACE,
            TK.SYMBOL,
            TK.VARIABLE,
        ]:
            node = UnitNode(cur)
        elif cur.kind in [TK.COMMAND]:
            node = self.parse_command(cur)
        else:
            raise UnexpectedNode(cur)
        if not allow_subsuper:
            return node
        accent = None
        subscript = None
        superscript = None
        if self.tok.kind == TK.ACCENT:
            self.advance()
            accent = self.parse_node(False)
        if self.tok.kind == TK.SUBSCRIPT:
            self.advance()
            subscript = self.parse_node(False)
        elif self.tok.kind == TK.SUPERSCRIPT:
            self.advance()
            superscript = self.parse_node(False)
        else:
            if accent is None:
                return node
            return SubSuperAccentScriptNode(node, subscript, superscript, accent)
        if self.tok.kind == TK.SUBSCRIPT:
            if subscript is not None:
                raise TooManySubSuperScripts("subscript")
            self.advance()
            subscript = self.parse_node(False)
        elif self.tok.kind == TK.SUPERSCRIPT:
            if superscript is not None:
                raise TooManySubSuperScripts("superscript")
            self.advance()
            superscript = self.parse_node(False)
        return SubSuperAccentScriptNode(node, subscript, superscript, accent)

    def parse_binary(self):
        a = self.parse_node()
        if self.tok.kind in [TK.FRACTION, TK.BINOMIAL]:
            op = self.tok
            self.advance()
            b = self.parse_node()
            return BinaryNode(a, b, op)
        return a

    def parse_group(self):
        nodes = []
        while self.tok.kind != TK.GROUP_CLOSE:
            node = self.parse_binary()
            nodes.append(node)
        self.advance()
        return GroupNode(nodes)

    def get_ast(self):
        return self.parse_group()

def get_tokens(source: str) -> list[Token]:
    return Lexer(str(source)).get_tokens()

def get_ast(source: str):
    tokens = get_tokens(source)
    if len(tokens) <= 0:
        return VoidNode()
    return Parser(tokens).get_ast()

def get_latex(ast: ASTNode) -> str:
    return "\\require{cancel}"+ast.get_latex()

def datex_to_latex(datex_source: str) -> str:
    return get_latex(get_ast(datex_source))
