import sqlite3
from random import randint
from typing import List, Optional, Protocol

from .data import BookDTO, LibraryDTO

#
# 2. Protocols
#


class LibraryRepository(Protocol):
    """Port de sortie pour les donnees"""

    def get_all(self) -> List[LibraryDTO]: ...
    def get_by_id(self, lib_id: int) -> Optional[LibraryDTO]: ...
    def add_book(self, title: str, lib_id: int) -> int | None: ...
    def edit_book(self, title: str, book_id: int) -> int | None: ...
    def create_lib(self, name: str, lib_id: int | None) -> int | None: ...


#
# 3. Adaptateurs (DAO)
#
class SQLiteLibraryDAO:
    def __init__(self, db_path: str = ":memory:"):
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self._setup_db()

    def _setup_db(self):
        cursor = self.conn.cursor()
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS libs (id INTEGER PRIMARY KEY, name TEXT)"
        )
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS books (id INTEGER PRIMARY KEY, title TEXT, lib_id INTEGER)"
        )

        # donnees de test
        cursor.execute(
            "INSERT INTO libs (name) SELECT 'Centrale 2' WHERE NOT EXISTS (SELECT 1 FROM libs)"
        )
        self.conn.commit()

    def get_all(self) -> List[LibraryDTO]:
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, name FROM libs")
        return [LibraryDTO(r[0], r[1]) for r in cursor.fetchall()]

    def get_by_id(self, lib_id: int) -> Optional[LibraryDTO]:
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, name FROM libs WHERE id = ?", (lib_id,))
        row = cursor.fetchone()

        if not row:
            return None

        cursor.execute("SELECT id, title FROM books WHERE lib_id = ?", (lib_id,))
        books = [BookDTO(r[0], r[1], lib_id) for r in cursor.fetchall()]
        return LibraryDTO(row[0], row[1], books)

    def create_lib(self, name, lib_id: int | None) -> int | None:
        cursor = self.conn.cursor()
        auto_id = (
            lib_id
            if lib_id
            else (
                randint(1, 100) + cursor.lastrowid
                if cursor.lastrowid
                else randint(1, 100)
            )
        )
        cursor.execute("INSERT INTO libs (id, name) VALUES (?, ?)", (auto_id, name))
        self.conn.commit()
        return cursor.lastrowid

    def add_book(self, title: str, lib_id: int) -> int | None:
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO books (title, lib_id) VALUES (?,?)", (title, lib_id)
        )
        self.conn.commit()
        return cursor.lastrowid

    def edit_book(self, title: str, book_id: int) -> int | None:
        cursor = self.conn.cursor()
        cursor.execute("UPDATE books SET title = ? WHERE id = ?", (title, book_id))
        self.conn.commit()
        return cursor.lastrowid
