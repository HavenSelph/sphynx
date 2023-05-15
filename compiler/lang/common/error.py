from compiler.lang.common.location import Span


class SphynxError(Exception):
    def print_error(self) -> None:
        """Prints the error to the terminal."""
        raise NotImplementedError()


class SpanError(SphynxError):
    def __init__(self, span: Span, message: str, flag_text: str="") -> None:
        self.span = span
        self.message = message
        self.flag_text = flag_text

    def print_error(self) -> None:
        """Prints the error to the terminal."""
        print(self.span)
        print(f"\u001b[31m{self.message}\u001b[0m")
        with open(self.span.filename, "r") as f:
            lines = [line.rstrip() for line in f.readlines()]
        context = 2
        min_line = max(0, self.span.start.line - context)
        max_line = min(len(lines), self.span.end.line + context)
        line_no_width = max(3, len(str(max_line)))
        for line_num, line in enumerate(lines[min_line:max_line], start=min_line):
            line_number = f"{(line_num + min_line):0>{line_no_width}}"
            if line_num + 1 == self.span.start.line:
                line = line[:self.span.start.column-1] + f"\u001b[31m{line[self.span.start.column-1:self.span.end.column-1]}\u001b[0m" + line[self.span.end.column-1:]
                print(f"{line_number} │{line}")
                connector = "└" if line_num+1 == max_line else "├"
                print(f"{' '*(line_no_width+1)}{connector}{'─' * (self.span.start.column-1)}\u001b[31m{'^' * (self.span.end.column - self.span.start.column)}\u001b[0m {self.flag_text}")
            else:
                print(f"{line_number} │{line}")


class GenericError(SphynxError):
    def __init__(self, message: str) -> None:
        self.message = message

    def print_error(self) -> None:
        print(f"\u001b[31m{self.message}\u001b[0m")
