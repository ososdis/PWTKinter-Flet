from typing import List

from models import LibraryDTO, LibraryRepository


#
# 4. Noyau : SERVICE
#
class LibraryService:
    def __init__(self, repo: LibraryRepository) -> None:
        self.repo = repo

    def fetch_libraries(self, search: str = "") -> List[LibraryDTO]:
        all_libs = self.repo.get_all()
        return [lib for lib in all_libs if search.lower() in lib.name.lower()]

    def get_details(self, lib_id: int) -> LibraryDTO | None:
        return self.repo.get_by_id(lib_id)

    def create_book(self, title: str, lib_id: int):
        if len(title) < 2:
            raise ValueError("Titre trop court !")
        return self.repo.add_book(title, lib_id)

    def add_new_lib(self, name):
        if len(name) < 2:
            raise ValueError("Nom trop court !")
        return self.repo.create_lib(name, lib_id=None)

    def edit_book(self, title: str, book_id: int):
        if len(title) < 2:
            raise ValueError("Titre trop court !")
        return self.repo.edit_book(title, book_id)
