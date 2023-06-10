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
        # todo: multiline errors don't work, fix that
        print(self.span)
        print(f"\u001b[31m{self.message}\u001b[0m")
        with open(self.span.filename, "r") as f:
            lines = [line.rstrip() for line in f.readlines()]
        context = 2
        start = self.span.start
        end = self.span.end
        min_line = max(0, start.line - context)
        max_line = min(len(lines), end.line + context)

        for line_n in range(min_line, max_line):
            line = lines[line_n]
            if start.line - 1 <= line_n < end.line:
                highlight_start = start.column - 1 if line_n == start.line - 1 else 0
                highlight_end = end.column - 1 if line_n == end.line - 1 else len(line)
                print(f"{line_n:0>3} | {line[:highlight_start]}\u001b[31m{line[highlight_start:highlight_end]}\u001b[0m{line[highlight_end:]}")
                if start.line == end.line:
                    print("    | " + "-" * highlight_start + "\u001b[31m" + "^" * (highlight_end - highlight_start) + "\u001b[0m")
                    if self.flag_text:
                        print("    | " + " " * highlight_start + "\u001b[31m" + self.flag_text + "\u001b[0m")
            else:
                print(f"{line_n:0>3} | {line}")


class GenericError(SphynxError):
    def __init__(self, message: str) -> None:
        self.message = message

    def print_error(self) -> None:
        print(f"\u001b[31m{self.message}\u001b[0m")
