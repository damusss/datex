from datex import get_ast, get_latex, get_tokens

import pyperclip

source = r"""
begin bmatrix
a_00    col  a_01   col  dots@-  col  a_{0n}   row
a_10    col  a_11   col  dots@-  col  a_{1n}   row
dots@|  col  dots@| col  dots@\\ col  dots@|   row
a_{m0}  col  a_{m1} col  dots@-  col  a_{m n}
end"""
print(source.strip())
tokens = get_tokens(source)
for tok in tokens:
    print(tok)
ast = get_ast(source)
print()
print(ast)
print()
latex = get_latex(ast)
print(latex)

pyperclip.copy(latex)


