# DaTex

DaTex is a Python library that is able to convert the DaTex syntax, a custom math domain language inspired by LaTex, into equivalent LaTex code that can be rendered by editors and applications like Obsidian.

### Syntax Summary
The language's syntax was designed to make LaTex be quicker to type to take notes during lessons and to replace parts of its verbosity while keeping the majority of the math features of LaTex.

Unlike LaTex, DaTex focuses entirely on math, and not general documents, and doesn't port obscure features or features from most LaTex extensions (though the set of features can be expanded in the future if necessary).

### Obsidian Integration
While the library can be used for any purpose, this repository is specifically tailored to provide an Obsidian plugin that can render LaTex math using a code block with the `datex` language.

### How to use
To use the library, clone this repository, as it is not distributed through PyPI. The library contains the `commands` module that contains the logic for syntax commands, the `error` module to except errors and the `datex` module that contains the lexer, parser, and translator implementations. The top-level of the library only exposes the most common function:
```python
from datex import datex_to_latex
```
Which returns a valid LaTex string from a valid DaTex string.

### How to add to Obsidian
After cloning the repositories,
Go inside `Path/To/Your/Vault/.obsidian/plugins` and either copy the `datex-obsidian-plugin` folder there or create a strong link to it. For example, on Windows you can run:
```bash
mklink /J "Path/To/Vault/.obsidian/plugins/datex-obsidian-plugin" "Path/To/Cloned/Repository/datex-obsidian-plugin"
```
Before trying to use the plugin, perform the following inside `Settings > Community plugins`:
- Click the vertical dots to the side of the `DaTex to LaTex Plugin` listed under `Installed plugins` and click `Settings`
- Edit both settings inputting the requested absolute paths
- Enable the plugin


You can now render DaTex math by using a `datex` code block:
````
```datex
e^{i pi} + 1 = 0
```
````