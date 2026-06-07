from dataclasses import dataclass, field
from typing import List

#
# 1. DTO
#


@dataclass
class BookDTO:
    id: int
    title: str
    library_id: int


@dataclass
class LibraryDTO:
    id: int
    name: str
    books: List[BookDTO] | None = field(default=None)
