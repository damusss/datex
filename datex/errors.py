class DatexSyntaxError(RuntimeError): ...


class UnterminatedTextLiteral(DatexSyntaxError):
    def __init__(self):
        super().__init__('" was never closed')


class TooManyOptionalParams(DatexSyntaxError):
    def __init__(self, tok):
        super().__init__(f"Too many optional parameters for {tok.render()}")


class UnexpectedNode(DatexSyntaxError):
    def __init__(self, tok):
        super().__init__(
            f"Expected a unit, a command, or a group, found something else: {tok}"
        )


class TooManySubSuperScripts(DatexSyntaxError):
    def __init__(self, word):
        super().__init__(f"Only one {word} is allowed per node")


class UnrecognizedAccent(DatexSyntaxError):
    def __init__(self, accent):
        super().__init__(f"'{accent}' is not a recognized accent")


class CommandError(DatexSyntaxError):
    ...