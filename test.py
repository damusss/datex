from mathdl.ast import get_ast

source = """
S(f(t)) "is true" if forall x in reals, x>=0\t exists k_c>0:2*x^{k_c} convolute f(t)=1
"""
print(source.strip())
ast = get_ast(source)
print()
print(ast)
