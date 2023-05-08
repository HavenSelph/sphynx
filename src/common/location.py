from dataclasses import dataclass


@dataclass
class Location:
  line: int
  column: int
  file: str

  def __str__(self):
    return f"{self.file}:{self.line}:{self.column}"


@dataclass
class Span:
  start: Location
  end: Location

  def __post_init__(self):
    self.file = self.start.file

  def extend(self, other: "Span") -> "Span":
    return Span(self.start, other.end)

  def __str__(self):
    return f"{self.start} - {self.end}"