import sys
from datex import datex_to_latex

source = sys.stdin.read()
latex = datex_to_latex(source)
print(latex)
