from __future__ import annotations


class Location:
    def __init__(self, filename: str, line: int, column: int, index: int) -> None:
        self.filename = filename
        self.line = line
        self.column = column
        self.index = index

    def __repr__(self) -> str:
        return f"{self.filename}:{self.line}:{self.column}"

    def __eq__(self, other: Location) -> bool:
        return self.filename == other.filename and self.line == other.line and self.column == other.column


class Span:
    def __init__(self, start: Location, end: Location) -> None:
        self.start = start
        self.end = end
        self.filename = start.filename

    def __repr__(self) -> str:
        if self.start == self.end:
            return f"{self.start}"
        return f"{self.start} - {self.end}"

    def extend(self, other: Span) -> Span:
        return Span(self.start, other.end)
