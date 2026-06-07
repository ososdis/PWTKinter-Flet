from typing import List

from models import BookDTO, LibraryRepository


#
# 4. Noyau : SERVICE
#
class BookService:
    def __init__(self, repo: LibraryRepository) -> None:
        self.repo = repo

    def create_book(self, title: str, lib_id: int):
        if len(title) < 2:
            raise ValueError("Titre trop court !")
        return self.repo.add_book(title, lib_id)
