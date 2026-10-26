from functools import partial
from datex.errors import CommandError


def mono_command(name: str, _, m: list):
    return "{" + f"\\{name}" + "{" + m[0].get_latex() + "}}"


def group_mono_command(name: str, _, m: list):
    return "{" + f"\\{name} " + m[0].get_latex() + "}"


def paren_command(name: str, _, m: list):
    return f"\\{name}{m[0].get_latex(True)}"


def root(_, m: list):
    return "{\\sqrt[" + m[0].get_latex() + "]{" + m[1].get_latex() + "}}"


def begin(o: list, m: list):
    environment = m[0].get_latex(True)
    latex = "{\\begin{" + environment + "}"
    for i, line in enumerate(o):
        if i != 0:
            latex += " \\\\ "
        latex += line.get_latex(True)
    return latex + "\\end{" + environment + "}}"


def substack(o: list, _):
    latex = "{\\substack{"
    for i, line in enumerate(o):
        if i != 0:
            latex += " \\\\ "
        latex += line.get_latex(True)
    return latex + "}}"


def neg(o: list, _):
    if len(o) <= 0:
        amount = 1
    else:
        if not hasattr(o[0], "tok"):
            raise CommandError(
                "The optional parameter of negative space has to be a number"
            )
        amount = int(o[0].tok.value)
    return "{" + "\\!" * amount + "}"


def dots(o: list, _):
    suffix = ""
    prefix = ""
    if len(o) <= 0:
        return "{\\dotso}"
    if not hasattr(o[0], "tok") or o[0].tok.value not in [
        "*",
        ",",
        "|",
        "+",
        "-",
        "int",
        "\\",
    ]:
        raise CommandError(
            "The optional parameter of dots must be either of: *+,|-\\int"
        )
    match o[0].tok.value:
        case "*":
            suffix = "m"
        case "int":
            suffix = "i"
        case "+":
            suffix = "b"
        case "-":
            prefix = "c"
        case "|":
            prefix = "v"
        case ",":
            suffix = "c"
        case "\\":
            prefix = "d"
    return "{\\" + prefix + "dots" + suffix + "}"


def cancel(o: list, m: list):
    prefix = ""
    if len(o) > 0:
        mode_node = o[0]
        if not hasattr(mode_node, "tok") or mode_node.tok.value not in ["x", "\\"]:
            raise CommandError(
                "The optional parameter of cancel must be either \\ or x"
            )
        if mode_node.tok.value == "x":
            prefix = "x"
        elif mode_node.tok.value == "\\":
            prefix = "b"
    return "{" + f"\\{prefix}cancel" + "{" + m[0].get_latex() + "}}"


boxed = partial(mono_command, "boxed")
phantom = partial(mono_command, "phantom")

sqrt = partial(mono_command, "sqrt")
cbrt = partial(mono_command, "sqrt[3]")

la = partial(paren_command, "left")
ra = partial(paren_command, "right")
lb = partial(paren_command, "bigl")
rb = partial(paren_command, "bigr")
lbb = partial(paren_command, "Bigl")
rbb = partial(paren_command, "Bigr")
lB = partial(paren_command, "biggl")
rB = partial(paren_command, "biggr")
lBB = partial(paren_command, "Biggl")
rBB = partial(paren_command, "Biggr")

full = partial(group_mono_command, "displaystyle")
inline = partial(group_mono_command, "textstyle")
script = partial(group_mono_command, "scriptstyle")
nestedscript = partial(group_mono_command, "scriptscriptstyle")

bbstyle = partial(mono_command, "mathbb")
bfstyle = partial(mono_command, "mathbf")
calstyle = partial(mono_command, "mathcal")
frakstyle = partial(mono_command, "mathfrak")
